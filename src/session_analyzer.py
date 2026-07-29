#!/usr/bin/env python3
"""
Hermes Session Analyzer — Agent Evolution 会话分析器

从 Hermes state.db (SQLite) 读取会话数据，提取：
1. 按工具统计成功/失败率和 Top 错误
2. 检测用户纠正信号
3. 检测重试循环
4. 检测技能缺口（反复出现但无对应技能的需求）

输出结构化数据，供 Agent Evolution 主分析器使用。

Usage:
    from src.session_analyzer import SessionAnalyzer
    analyzer = SessionAnalyzer()
    result = analyzer.analyze(days=7)
    analyzer.print_dashboard(result)

Inspired by: https://github.com/Yonkoo11/hermes-dojo (monitor.py)
"""

import json
import os
import re
import sqlite3
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── 默认路径 ──────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
DB_PATH = HERMES_HOME / "state.db"


# ── 错误检测模式（工具响应中的错误信号）────────────────────
# 注意：Hermes 工具响应通常是 JSON 格式，包含 "success": true 等字段。
# 我们只匹配真正的执行时错误，不匹配 JSON 字典键名。

# (pattern, category)：优先匹配的特定错误
# 放在前面，长字符串优先匹配
ERROR_SIGNATURES: list[tuple[str, str]] = [
    # 文件/路径错误
    ("command not found", "command_not_found"),
    ("no such file or directory", "path_not_found"),
    ("permission denied", "permission"),
    ("No such file", "path_not_found"),
    ("ENOENT", "path_not_found"),
    ("EACCES", "permission"),
    ("ETIMEDOUT", "timeout"),
    # 网络错误
    ("timeout", "timeout"),
    ("Connection refused", "connection"),
    ("connection refused", "connection"),
    ("rate limit", "rate_limit"),
    ("Rate Limit", "rate_limit"),
    ("429 Too Many Requests", "rate_limit"),
    ("404 Not Found", "not_found"),
    ("500 Internal Server", "server_error"),
    ("502 Bad Gateway", "server_error"),
    ("503 Service Unavailable", "server_error"),
    ("unauthorized", "auth"),
    ("access denied", "permission"),
    # 语法/参数错误
    ("syntax error", "syntax_error"),
    ("is required", "missing_parameter"),
    ("missing required", "missing_parameter"),
    ("must be provided", "missing_parameter"),
    # 通用错误
    ("Traceback", "runtime_error"),
    ("Exception:", "runtime_error"),
]

# 需要排除的 false positive 模式（在 JSON 工具响应中常见的非错误文本）
FALSE_POSITIVE_EXCLUDE = [
    # JSON 成功响应中的字段名
    '"success": true',
    '"success": false',    # 这是正常的布尔字段
    '"errors": ',          # 这是字段名不是错误
    'failed to open',      # 先确认是实际错误
    # 非错误的 "could not" / "unable to"
    "could not be empty",
    "could not be None",
    # skill_view 返回的文本中的内容
    "---",
    "name:",
    "description:",
    "# ",
]


# ── 用户纠正检测模式 ──────────────────────────────────────
CORRECTION_PATTERNS = [
    r"(?i)^不[对是好的]",
    r"(?i)^不是[这那]",
    r"(?i)错了",
    r"(?i)不对",
    r"(?i)wrong",
    r"(?i)not what I",
    r"(?i)I meant",
    r"(?i)you misunderstood",
    r"(?i)incorrect",
    r"(?i)fix (this|that|it)",
    r"(?i)try again",
    r"(?i)that broke",
    r"(?i)doesn't work",
    r"(?i)not working",
    r"(?i)why did you",
    r"(?i)不要",
    r"(?i)不对",
    r"(?i)不是这样",
    r"(?i)不是这个",
    r"(?i)搞错了",
    r"(?i)弄错了",
    r"(?i)谁让你",
    r"(?i)我说的是",
    r"(?i)我的意思是",
    r"(?i)stop",
    r"(?i)undo",
    r"(?i)revert",
]


# ── 技能缺口检测关键词 ─────────────────────────────────────
# 这些能力如果用户经常要求但没有对应技能，标记为缺口
SKILL_GAP_KEYWORDS = {
    "CSV": ["csv", "excel", "xlsx", "表格", "电子表格", "spreadsheet"],
    "PDF处理": ["pdf", "提取pdf", "pdf转"],
    "数据分析": ["分析数据", "数据可视化", "chart", "plot", "图表"],
    "图片处理": ["图片", "image", "截图", "ocr", "识别图片"],
    "定时任务": ["定时", "cron", "每天", "每小", "每分", "定期"],
    "网络请求": ["curl", "http", "api请求", "fetch"],
    "文件批量": ["批量", "多个文件", "遍历", "所有文件"],
    "代码审查": ["review", "code review", "审查代码", "代码检查"],
    "数据库": ["mysql", "postgres", "redis", "sqlite", "查询数据库"],
    "部署": ["部署", "deploy", "发布", "上线"],
}


class SessionAnalyzer:
    """Hermes 会话分析器：读取 state.db，输出结构化性能数据。"""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self._conn = None

    # ── 数据库连接 ────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        """连接 state.db（只读模式）。"""
        if self._conn is None:
            if not self.db_path.exists():
                raise FileNotFoundError(f"state.db 不存在: {self.db_path}")
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── 核心分析 ───────────────────────────────────────────

    def analyze(self, days: int = 7) -> dict:
        """
        分析最近 N 天的会话数据。

        Args:
            days: 分析的天数范围（默认 7 天）

        Returns:
            dict: 结构化分析结果
        """
        tm_start = time.time()
        conn = self._connect()
        cutoff = tm_start - days * 86400

        result = {
            "timestamp": tm_start,
            "days_analyzed": days,
            "sessions_analyzed": 0,
            "total_tool_calls": 0,
            "total_errors": 0,
            "overall_success_rate": 0.0,
            "per_tool_stats": [],
            "user_corrections": 0,
            "correction_samples": [],
            "retry_loops": [],
            "skill_gaps": [],
            "total_messages": 0,
            "sessions": [],
        }

        # 1. 获取会话列表
        sessions = self._get_sessions(cutoff)
        result["sessions_analyzed"] = len(sessions)
        result["sessions"] = [
            {
                "id": s["id"],
                "source": s["source"],
                "model": s["model"],
                "tool_calls": s["tool_call_count"],
                "messages": s["message_count"],
                "started_at": s["started_at"],
            }
            for s in sessions[:20]
        ]

        if not sessions:
            result["overall_success_rate"] = 100.0
            return result

        # 2. 分析工具调用
        per_tool = defaultdict(lambda: {"total": 0, "errors": 0, "error_samples": []})

        # 按会话分析，便于检测重试循环
        for session in sessions:
            sid = session["id"]
            messages = self._get_session_messages(sid)

            # 提取工具调用的序列（role=tool 且有 tool_name）
            tool_msgs = [
                {
                    "id": m["id"],
                    "tool_name": m["tool_name"],
                    "content": m["content"] or "",
                    "timestamp": m["timestamp"],
                }
                for m in messages
                if m["role"] in ("tool",) and m["tool_name"] and m["tool_name"].strip()
            ]

            # 统计工具
            for tm in tool_msgs:
                tool_name = tm["tool_name"].strip()
                per_tool[tool_name]["total"] += 1
                result["total_tool_calls"] += 1

                # 检查是否有错误
                content = tm["content"]
                error = self._detect_error(content)
                if error:
                    per_tool[tool_name]["errors"] += 1
                    result["total_errors"] += 1
                    if len(per_tool[tool_name]["error_samples"]) < 3:
                        per_tool[tool_name]["error_samples"].append(error)

            # 检测重试循环：30 秒内同一工具调用 >= 2 次
            retries = self._detect_retry_loops(tool_msgs)
            result["retry_loops"].extend(
                {"tool": r["tool"], "count": r["count"], "session_id": sid}
                for r in retries
            )

        # 3. 用户纠正检测
        corrections = self._detect_corrections(sessions)
        result["user_corrections"] = len(corrections)
        result["correction_samples"] = [
            {
                "session_id": c["session_id"],
                "content": c["content"][:200],
            }
            for c in corrections[:5]
        ]

        # 4. 技能缺口检测
        skill_gaps = self._detect_skill_gaps(sessions)
        result["skill_gaps"] = skill_gaps[:10]

        # 5. 计算总消息数
        result["total_messages"] = sum(s["message_count"] or 0 for s in sessions)

        # 6. 计算各工具统计
        total_all = sum(v["total"] for v in per_tool.values())
        total_errors = sum(v["errors"] for v in per_tool.values())
        overall = ((total_all - total_errors) / total_all * 100) if total_all > 0 else 0
        result["overall_success_rate"] = round(overall, 1)

        for tool_name, stats in sorted(per_tool.items(), key=lambda x: -x[1]["total"]):
            if stats["total"] == 0:
                continue
            rate = ((stats["total"] - stats["errors"]) / stats["total"] * 100)
            top_error = self._get_top_error(stats["error_samples"])
            result["per_tool_stats"].append({
                "tool": tool_name,
                "total": stats["total"],
                "errors": stats["errors"],
                "success_rate": round(rate, 1),
                "top_error": top_error,
            })

        return result

    # ── 内部方法 ────────────────────────────────────────────

    def _get_sessions(self, cutoff: float) -> list[sqlite3.Row]:
        """获取指定时间之后的会话。"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            """SELECT id, source, model, tool_call_count, message_count,
                      started_at, ended_at
               FROM sessions
               WHERE started_at >= ?
               ORDER BY started_at DESC""",
            (cutoff,),
        )
        return c.fetchall()

    def _get_session_messages(self, session_id: str) -> list[sqlite3.Row]:
        """获取指定会话的所有消息，按时间正序。"""
        conn = self._connect()
        c = conn.cursor()
        c.execute(
            """SELECT id, role, content, tool_name, tool_call_id,
                      tool_calls, timestamp
               FROM messages
               WHERE session_id = ?
               ORDER BY id ASC""",
            (session_id,),
        )
        return c.fetchall()

    def _detect_error(self, content: str) -> str | None:
        """检测消息内容中是否包含执行期错误。返回错误类型。"""
        # 先排除已知的 false positive
        for exclude in FALSE_POSITIVE_EXCLUDE:
            if exclude in content:
                return None

        # 按优先级匹配已知错误签名
        for pattern, category in ERROR_SIGNATURES:
            if pattern in content:
                return category
        return None

    def _detect_retry_loops(
        self, tool_msgs: list[dict], window: float = 30.0, min_count: int = 4
    ) -> list[dict]:
        """检测 30 秒内同一工具的重复调用（连续 4 次以上视为重试循环）。"""
        # 按工具名分组并排序
        by_tool: dict[str, list[dict]] = defaultdict(list)
        for tm in tool_msgs:
            by_tool[tm["tool_name"]].append(tm)

        retries = []
        for tool_name, msgs in by_tool.items():
            msgs.sort(key=lambda x: x["timestamp"])
            count = 1
            for i in range(1, len(msgs)):
                if msgs[i]["timestamp"] - msgs[i - 1]["timestamp"] <= window:
                    count += 1
                else:
                    if count >= min_count:
                        retries.append({"tool": tool_name, "count": count})
                    count = 1
            if count >= min_count:
                retries.append({"tool": tool_name, "count": count})

        return retries

    def _detect_corrections(self, sessions: list[sqlite3.Row]) -> list[dict]:
        """检测用户纠正信号（排除系统注入消息和技能调用提示）。"""
        corrections = []
        conn = self._connect()
        c = conn.cursor()

        # 排除模式：系统注入的消息开头
        system_prefixes = [
            "[IMPORTANT:",
            "[SYSTEM:",
            "[SKILL:",
            "The user has invoked",
            "You are powered by",
            "You run on Hermes Agent",
            "Before replying",
            "Available skills",
        ]

        for session in sessions:
            c.execute(
                """SELECT id, content, timestamp
                   FROM messages
                   WHERE session_id = ? AND role = 'user'
                     AND content IS NOT NULL
                   ORDER BY id ASC""",
                (session["id"],),
            )
            for row in c.fetchall():
                content = row["content"].strip()

                # 跳过系统注入消息
                if any(content.startswith(p) for p in system_prefixes):
                    continue
                # 跳过过短的消息（通常不是纠正）
                if len(content) < 5:
                    continue

                for pattern in CORRECTION_PATTERNS:
                    if re.search(pattern, content):
                        corrections.append({
                            "session_id": session["id"],
                            "content": content,
                            "timestamp": row["timestamp"],
                        })
                        break

        return corrections

    def _detect_skill_gaps(self, sessions: list[sqlite3.Row]) -> list[dict]:
        """检测技能缺口：用户反复请求但没有对应技能的能力。"""
        # 先获取已有技能列表
        installed_skills = self._get_installed_skills()
        # 展平为小写关键词集
        skill_keywords = set()
        for sk in installed_skills:
            parts = re.split(r"[-_\s]", sk.lower())
            skill_keywords.update(parts)

        # 扫描用户消息
        gap_counts: dict[str, int] = defaultdict(int)
        conn = self._connect()
        c = conn.cursor()

        for session in sessions:
            c.execute(
                """SELECT content FROM messages
                   WHERE session_id = ? AND role = 'user'
                     AND content IS NOT NULL
                   ORDER BY id ASC""",
                (session["id"],),
            )
            for row in c.fetchall():
                content = row["content"].lower()
                for capability, keywords in SKILL_GAP_KEYWORDS.items():
                    for kw in keywords:
                        if kw in content:
                            # 检查是否已有对应技能
                            is_covered = any(sk_kw in kw for sk_kw in skill_keywords)
                            if not is_covered:
                                gap_counts[capability] += 1
                            break

        return [
            {"capability": name, "requests": count}
            for name, count in sorted(gap_counts.items(), key=lambda x: -x[1])
            if count >= 2
        ]

    def _get_installed_skills(self) -> list[str]:
        """扫描 ~/.hermes/skills 获取已安装技能名称。"""
        skills_dir = HERMES_HOME / "skills"
        if not skills_dir.exists():
            return []

        skills = []
        for item in skills_dir.iterdir():
            if item.is_dir():
                # 一级目录（分类下的技能）
                for sub in item.iterdir():
                    if sub.is_dir() and (sub / "SKILL.md").exists():
                        skills.append(sub.name)
            elif item.is_dir() and (item / "SKILL.md").exists():
                # 顶级技能
                skills.append(item.name)
        return skills

    def _get_top_error(self, samples: list[str]) -> str:
        """从错误样本中提取最常见的错误类型。"""
        if not samples:
            return ""
        # 直接返回错误类型（category）
        for sample in samples:
            if sample:
                return sample
        return ""

    # ── 输出格式 ────────────────────────────────────────────

    def print_dashboard(self, data: dict):
        """打印可读的分析仪表盘。"""
        if data.get("sessions_analyzed", 0) == 0:
            print(data.get("message", "未找到会话数据。"))
            return

        cutoff_ts = time.time() - data["days_analyzed"] * 86400
        cutoff_date = datetime.fromtimestamp(cutoff_ts).strftime("%Y-%m-%d")

        print("=" * 60)
        print("  AGENT EVOLUTION — SESSION 分析")
        print("=" * 60)
        print(f"  分析会话: {data['sessions_analyzed']} (自 {cutoff_date})")
        print(f"  工具调用总数: {data['total_tool_calls']}")
        print(f"  消息总数: {data['total_messages']}")
        print(f"  总体成功率: {data['overall_success_rate']}%")
        print()

        # Top 弱工具
        weak = [t for t in data.get("per_tool_stats", []) if t["errors"] > 0]
        if weak:
            print("  📉 弱工具 (有错误记录):")
            print("  " + "-" * 56)
            for t in weak[:10]:
                bar = "█" * max(1, min(20, int(t["success_rate"] / 5)))
                print(
                    f"  {t['tool']:25s} {t['success_rate']:5.1f}% "
                    f"{bar} ({t['errors']}/{t['total']})"
                )
                if t["top_error"]:
                    print(f"  {'':25s} → {t['top_error']}")
            print()

        # 用户纠正
        if data.get("user_corrections", 0) > 0:
            print(f"  👤 用户纠正: {data['user_corrections']} 次")
            for c in data.get("correction_samples", [])[:3]:
                print(f"    • \"{c['content'][:60]}...\"")
            print()

        # 重试循环
        if data.get("retry_loops"):
            print(f"  🔄 重试循环: {len(data['retry_loops'])} 个")
            for r in data["retry_loops"][:5]:
                print(f"    • {r['tool']}: 连续调用 {r['count']} 次")
            print()

        # 技能缺口
        if data.get("skill_gaps"):
            print("  🆕 技能缺口:")
            for g in data["skill_gaps"]:
                print(f"    • {g['capability']}: 被请求 {g['requests']} 次，无对应技能")
            print()

        print("=" * 60)


# ── CLI 入口 ────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Hermes Session Analyzer — Agent Evolution"
    )
    parser.add_argument(
        "--days", type=int, default=7, help="分析天数 (默认: 7)"
    )
    parser.add_argument(
        "--json", action="store_true", help="JSON 格式输出"
    )
    args = parser.parse_args()

    analyzer = SessionAnalyzer()
    data = analyzer.analyze(days=args.days)

    if args.json:
        # 确保 Counter 等可序列化
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    else:
        analyzer.print_dashboard(data)
