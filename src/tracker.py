#!/usr/bin/env python3
"""
Agent Evolution — 学习曲线追踪器 (Learning Curve Tracker)

持久化每日性能快照并生成趋势分析 + sparkline 可视化。

Usage:
    python3 -m src.tracker save           # 保存今日快照（基于 session_analyzer）
    python3 -m src.tracker history        # 显示学习曲线
    python3 -m src.tracker history --days 30  # 显示最近 30 天
    python3 -m src.tracker trend           # 显示趋势总结

灵感来源: https://github.com/Yonkoo11/hermes-dojo (tracker.py)
"""

import json
import os
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── 路径 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "v2" / "output"
METRICS_FILE = DATA_DIR / "metrics-history.json"

# Unicode 火花线条块
SPARK_CHARS = " ▁▂▃▄▅▆▇█"


def _now_ts() -> float:
    return time.time()


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _datetime_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


# ── 核心类 ─────────────────────────────────────────────


class LearningTracker:
    """学习曲线追踪器：保存/读取/展示每日性能数据。"""

    def __init__(self, metrics_path: str | Path | None = None):
        self.metrics_path = Path(metrics_path) if metrics_path else METRICS_FILE
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    # ── 数据读写 ───────────────────────────────────────

    def load_history(self) -> list[dict]:
        """加载历史指标。"""
        if not self.metrics_path.exists():
            return []
        try:
            with open(self.metrics_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return []

    def save_snapshot(
        self,
        session_data: dict = None,
        improvements: list[dict] = None,
    ) -> dict:
        """
        保存今日快照。

        Args:
            session_data: session_analyzer.analyze() 的返回结果
            improvements: 本次应用的改进项列表（可选）

        Returns:
            dict: 保存的快照
        """
        history = self.load_history()

        # 如果未提供 session_data，尝试从 session_analyzer 获取
        if session_data is None:
            try:
                sys.path.insert(0, str(PROJECT_ROOT))
                from src.session_analyzer import SessionAnalyzer

                sa = SessionAnalyzer()
                session_data = sa.analyze(days=7)
                sa.close()
            except Exception as e:
                print(f"  ⚠️ 无法获取 session 数据: {e}")
                session_data = {}

        # Guard：如果 session 数据为空（0 会话），不覆盖已有的有意义历史
        sessions_count = session_data.get("sessions_analyzed", 0)
        if sessions_count == 0 and history:
            print("  ⚠️ session 数据为空（0 会话），跳过快照保存以保护已有历史")
            return history[-1]  # 返回上次快照

        # 构建快照
        weak_tools = [
            {"tool": t["tool"], "success_rate": t["success_rate"], "errors": t["errors"]}
            for t in session_data.get("per_tool_stats", [])
            if t["errors"] > 0
        ]

        snapshot = {
            "timestamp": _now_ts(),
            "date": _today_str(),
            "datetime": _datetime_str(),
            "sessions_analyzed": session_data.get("sessions_analyzed", 0),
            "total_tool_calls": session_data.get("total_tool_calls", 0),
            "overall_success_rate": session_data.get("overall_success_rate", 0),
            "total_errors": session_data.get("total_errors", 0),
            "user_corrections": session_data.get("user_corrections", 0),
            "skill_gaps": len(session_data.get("skill_gaps", [])),
            "retry_loops": len(session_data.get("retry_loops", [])),
            "weak_tools": weak_tools[:10],
        }

        if improvements:
            snapshot["improvements_made"] = len(improvements)

        # 去重：如果今天已有快照，更新它
        today = _today_str()
        existing_idx = None
        for i, snap in enumerate(history):
            if snap.get("date") == today:
                existing_idx = i
                break

        if existing_idx is not None:
            history[existing_idx] = snapshot
        else:
            history.append(snapshot)

        # 保留最近 90 天
        cutoff = _now_ts() - 90 * 86400
        history = [h for h in history if h.get("timestamp", 0) > cutoff]

        # 原子写入
        self._atomic_write(history)

        return snapshot

    def _atomic_write(self, data: list):
        """写入 tmp 文件后 rename，防止写入中断损坏。"""
        tmp_file = self.metrics_path.with_suffix(".tmp")
        with open(tmp_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp_file.replace(self.metrics_path)

    # ── 趋势分析 ───────────────────────────────────────

    def compute_trend(self, history: list[dict] = None, window: int = 7) -> dict:
        """计算趋势指标。"""
        if history is None:
            history = self.load_history()

        if len(history) == 0:
            return {"has_data": False}

        # 按日期排序
        sorted_history = sorted(history, key=lambda x: x.get("date", ""))

        latest = sorted_history[-1]
        oldest = sorted_history[0]

        # 从倒数第 window 天取基线
        baseline_idx = max(0, len(sorted_history) - window - 1)
        baseline = sorted_history[baseline_idx] if baseline_idx < len(sorted_history) - 1 else None

        # 最近 window 天的数据（含今天）
        recent = sorted_history[-window:] if len(sorted_history) >= window else sorted_history

        current_rate = latest.get("overall_success_rate", 0)
        baseline_rate = baseline.get("overall_success_rate", 0) if baseline else current_rate

        # 趋势方向
        delta = current_rate - baseline_rate
        if delta > 0:
            direction = "📈"
        elif delta < 0:
            direction = "📉"
        else:
            direction = "➡️"

        # 近 window 天的变化率
        rates = [h.get("overall_success_rate", 0) for h in recent]
        directions = []
        for i in range(1, len(rates)):
            if rates[i] > rates[i - 1]:
                directions.append("up")
            elif rates[i] < rates[i - 1]:
                directions.append("down")
            else:
                directions.append("flat")

        up_days = directions.count("up")
        down_days = directions.count("down")

        # 改进项趋势
        corrections_trend = self._compute_field_trend(sorted_history, "user_corrections")
        retry_trend = self._compute_field_trend(sorted_history, "retry_loops")
        errors_trend = self._compute_field_trend(sorted_history, "total_errors")

        return {
            "has_data": True,
            "total_snapshots": len(sorted_history),
            "days_span": (len(sorted_history) - 1) if len(sorted_history) > 1 else 0,
            "current_rate": current_rate,
            "baseline_rate": baseline_rate,
            "delta": round(delta, 1),
            "direction": direction,
            "window": window,
            "up_days": up_days,
            "down_days": down_days,
            "corrections": corrections_trend,
            "retry_loops": retry_trend,
            "errors": errors_trend,
            "latest": latest,
            "oldest": oldest,
        }

    def _compute_field_trend(self, history: list, field: str) -> dict:
        """计算某个字段的趋势（下降=好）。"""
        if len(history) < 2:
            return {"current": 0, "baseline": 0, "delta": 0, "direction": "➡️"}

        current = history[-1].get(field, 0)
        baseline = history[0].get(field, 0)
        delta = baseline - current  # 正数=改善（下降了）

        if delta > 0:
            direction = "✅"
        elif delta < 0:
            direction = "⚠️"
        else:
            direction = "➡️"

        return {
            "current": current,
            "baseline": baseline,
            "delta": delta,
            "direction": direction,
        }

    # ── 可视化 ───────────────────────────────────────────

    def sparkline(self, values: list[float], width: int = 10) -> str:
        """生成 Unicode sparkline。"""
        if not values:
            return ""

        # 取最近 width 个
        if len(values) > width:
            values = values[-width:]

        min_v, max_v = min(values), max(values)
        span = max_v - min_v

        if span == 0:
            return "█" * len(values)

        # 映射到 0-8 的字符索引
        return "".join(
            SPARK_CHARS[min(8, int((v - min_v) / span * 8))] for v in values
        )

    def print_history(self, days: int = None):
        """打印学习曲线仪表盘。"""
        history = self.load_history()

        if not history:
            print("📊 尚无指标历史数据。请先运行进化分析。")
            return

        # 排序
        sorted_h = sorted(history, key=lambda x: x.get("date", ""))

        # 过滤天数
        if days and days < len(sorted_h):
            sorted_h = sorted_h[-days:]

        print("=" * 62)
        print("  📈 AGENT EVOLUTION — 学习曲线")
        print("=" * 62)
        print()
        print(f"  {'日期':<14} {'成功率':>8} {'工具调用':>8} {'错误':>6} {'纠正':>6} {'重试':>6}")
        print("  " + "-" * 56)

        for snap in sorted_h[-30:]:  # 最多 30 行
            date = snap.get("date", "?")[-5:]  # 只显示 MM-DD
            rate = snap.get("overall_success_rate", 0)
            calls = snap.get("total_tool_calls", 0)
            errors = snap.get("total_errors", 0)
            corrections = snap.get("user_corrections", 0)
            retries = snap.get("retry_loops", 0)
            print(f"  {date:<14} {rate:>7.1f}% {calls:>8} {errors:>6} {corrections:>6} {retries:>6}")

        # 趋势计算
        trend = self.compute_trend(sorted_h)
        if trend["has_data"] and trend["days_span"] > 0:
            print()
            print(f"  📊 趋势 (过去 {trend['window']} 天):")
            print(f"     成功率: {trend['baseline_rate']:.1f}% → {trend['current_rate']:.1f}% "
                  f"({'+' if trend['delta'] >= 0 else ''}{trend['delta']:.1f}%) {trend['direction']}")

            # Sparkline
            rates = [h.get("overall_success_rate", 0) for h in sorted_h]
            spk = self.sparkline(rates, width=14)
            print(f"     走势: [{spk}]")

            # 纠正趋势
            c = trend["corrections"]
            print(f"     用户纠正: {c['current']} (基线 {c['baseline']}) {c['direction']}")

            # 重试趋势
            r = trend["retry_loops"]
            print(f"     重试循环: {r['current']} (基线 {r['baseline']}) {r['direction']}")

            # 错误趋势
            e = trend["errors"]
            print(f"     工具错误: {e['current']} (基线 {e['baseline']}) {e['direction']}")

        print()
        print(f"  📁 {len(history)} 个快照 | 跨度 {trend.get('days_span', 0)} 天")
        print("=" * 62)

    def print_trend_summary(self) -> str:
        """生成趋势总结文本（用于报告）。"""
        history = self.load_history()
        if not history:
            return "尚无历史数据。"

        trend = self.compute_trend(history)
        sorted_h = sorted(history, key=lambda x: x.get("date", ""))
        rates = [h.get("overall_success_rate", 0) for h in sorted_h]
        spk = self.sparkline(rates, width=14)

        lines = [
            f"📈 **学习曲线** (跨度 {trend['days_span']} 天, {trend['total_snapshots']} 个快照)",
            f"",
            f"  成功率: {trend['baseline_rate']:.1f}% → {trend['current_rate']:.1f}% "
            f"({'+' if trend['delta'] >= 0 else ''}{trend['delta']:.1f}%) {trend['direction']}",
            f"  走势: [{spk}]",
        ]

        if trend["up_days"] > 0 or trend["down_days"] > 0:
            total = trend["up_days"] + trend["down_days"]
            lines.append(
                f"  近 {trend['window']} 天: {trend['up_days']} 天↑ / {trend['down_days']} 天↓"
            )

        c = trend["corrections"]
        lines.append(
            f"  用户纠正: {c['current']} 次{c['direction']} "
            f"(基线 {c['baseline']} 次, {'改善' if c['delta'] > 0 else '恶化' if c['delta'] < 0 else '持平'})"
        )

        r = trend["retry_loops"]
        lines.append(
            f"  重试循环: {r['current']} 个{r['direction']} "
            f"(基线 {r['baseline']} 个, {'改善' if r['delta'] > 0 else '恶化' if r['delta'] < 0 else '持平'})"
        )

        return "\n".join(lines)


# ── CLI 入口 ─────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent Evolution — 学习曲线追踪器"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # save
    save_p = sub.add_parser("save", help="保存今日快照")
    save_p.add_argument("--json", action="store_true", help="JSON 输出")

    # history
    hist_p = sub.add_parser("history", help="显示学习曲线")
    hist_p.add_argument("--days", type=int, default=None, help="显示最近 N 天")
    hist_p.add_argument("--json", action="store_true", help="JSON 输出")

    # trend
    trend_p = sub.add_parser("trend", help="趋势总结")
    trend_p.add_argument("--json", action="store_true", help="JSON 输出")

    args = parser.parse_args()

    tracker = LearningTracker()

    if args.command == "save":
        snapshot = tracker.save_snapshot()
        if args.json:
            print(json.dumps(snapshot, indent=2, ensure_ascii=False))
        else:
            rate = snapshot.get("overall_success_rate", 0)
            print(f"✅ 快照已保存: {snapshot['date']} — {rate}% 成功率")

    elif args.command == "history":
        if args.json:
            print(json.dumps(tracker.load_history(), indent=2, ensure_ascii=False))
        else:
            tracker.print_history(days=args.days)

    elif args.command == "trend":
        if args.json:
            print(json.dumps(tracker.compute_trend(), indent=2, ensure_ascii=False))
        else:
            print(tracker.print_trend_summary())


if __name__ == "__main__":
    main()
