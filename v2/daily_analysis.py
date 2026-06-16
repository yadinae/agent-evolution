#!/usr/bin/env python3
"""
Agent Evolution v2 每日分析 — 纯 Python 实现（含 AutoFixer）

分析 Hermes 系统状态 → 生成改进计划 → 自动执行可修复项
"""
import os
import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict

HERMES_HOME = Path(os.path.expanduser("~/.hermes"))
CRON_OUTPUT_DIR = HERMES_HOME / "cron" / "output"
SKILLS_DIR = HERMES_HOME / "skills"
SCRIPTS_DIR = HERMES_HOME / "scripts"
EVOLUTION_DIR = Path(os.path.expanduser("~/projects/agent-evolution")) / "v2" / "output"
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

now = datetime.now()
today_str = now.strftime("%Y-%m-%d")
now_str = now.strftime("%Y-%m-%d %H:%M")


# ============================================================================
# 1. Cron 任务健康分析
# ============================================================================

def analyze_cron_health():
    results = {}
    if not CRON_OUTPUT_DIR.exists():
        return {"error": "Cron 输出目录不存在", "dir": str(CRON_OUTPUT_DIR)}

    for job_dir in sorted(CRON_OUTPUT_DIR.iterdir()):
        if not job_dir.is_dir():
            continue
        job_id = job_dir.name
        output_files = sorted(job_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)

        if not output_files:
            results[job_id] = {"status": "unknown", "reason": "无输出文件", "recent_runs": 0}
            continue

        recent_files = output_files[:7]
        run_results = []
        ok_count = 0

        for f in recent_files:
            try:
                content = f.read_text(encoding="utf-8")
            except Exception:
                run_results.append({"date": f.name[:10], "status": "error", "size_kb": 0})
                continue

            status = _extract_run_status(content)
            if status == "ok":
                ok_count += 1
            run_results.append({
                "date": f.name[:10],
                "file": f.name,
                "status": status,
                "size_kb": round(f.stat().st_size / 1024, 1)
            })

        total = len(run_results)
        if total == 0:
            job_status = "unknown"
        elif ok_count == total:
            job_status = "healthy"
        elif ok_count >= total * 0.7:
            job_status = "degraded"
        else:
            job_status = "failing"

        error_patterns = _extract_error_patterns([f.read_text(encoding="utf-8") for f in recent_files])

        results[job_id] = {
            "status": job_status,
            "recent_runs": run_results,
            "success_rate": round(ok_count / total, 2) if total > 0 else 0,
            "error_patterns": error_patterns[:5]
        }

    return {
        "timestamp": now.isoformat(),
        "total_jobs": len(results),
        "healthy": sum(1 for r in results.values() if r.get("status") == "healthy"),
        "degraded": sum(1 for r in results.values() if r.get("status") == "degraded"),
        "failing": sum(1 for r in results.values() if r.get("status") == "failing"),
        "jobs": results
    }


def _extract_run_status(content):
    if "## Response" in content:
        response_part = content.split("## Response", 1)[-1]
        if any(kw in response_part for kw in ["Traceback", "FAILED", "terminated"]):
            return "error"
        return "ok"
    return "ok"


def _extract_error_patterns(contents):
    all_errors = []
    for content in contents:
        if "## Response" in content:
            text = content.split("## Response", 1)[-1]
        else:
            text = content[-3000:]
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if line.strip().startswith("|") or line.strip().startswith("-"):
                continue
            if line.strip().startswith("##"):
                continue
            if any(kw in line for kw in ["Traceback", "FAILED", "Error:"]):
                start = max(0, i - 1)
                end = min(len(lines), i + 3)
                context = "\n".join(lines[start:end])
                all_errors.append(context[:300])
    error_counts = Counter(all_errors)
    return [{"pattern": p, "count": c} for p, c in error_counts.most_common(10) if c >= 2]


# ============================================================================
# 2. 技能库质量审计
# ============================================================================

def analyze_skills():
    if not SKILLS_DIR.exists():
        return {"error": "技能目录不存在", "dir": str(SKILLS_DIR)}

    total_skills = 0
    with_doc = 0
    without_doc = []
    by_category = defaultdict(list)
    empty_skills = []
    outdated_skills = []

    for cat_dir in sorted(SKILLS_DIR.iterdir()):
        if not cat_dir.is_dir():
            continue
        # ★ 修复：跳过 . 开头的系统目录（如 .curator_backups）
        if cat_dir.name.startswith("."):
            continue
        category = cat_dir.name

        for skill_dir in sorted(cat_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            if skill_dir.name in ("references", "templates", "scripts", "assets", ".hub"):
                continue
            if skill_dir.name.startswith("."):
                continue

            total_skills += 1
            skill_info = {
                "name": f"{category}/{skill_dir.name}",
                "category": category,
                "path": str(skill_dir)
            }

            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                with_doc += 1
                try:
                    content = skill_md.read_text(encoding="utf-8")
                except Exception:
                    content = ""

                if len(content.strip()) < 100:
                    empty_skills.append(skill_info)

                mtime = datetime.fromtimestamp(skill_md.stat().st_mtime)
                if (now - mtime).days > 30:
                    skill_info["last_modified"] = mtime.strftime("%Y-%m-%d")
                    skill_info["days_since_update"] = (now - mtime).days
                    outdated_skills.append(skill_info)
            else:
                without_doc.append(skill_info)

            by_category[category].append(skill_info)

    return {
        "timestamp": now.isoformat(),
        "total_skills": total_skills,
        "with_documentation": with_doc,
        "without_documentation": len(without_doc),
        "missing_docs": [{"name": s["name"]} for s in without_doc[:10]],
        "empty_skills": [{"name": s["name"]} for s in empty_skills[:5]],
        "outdated_skills": [
            {"name": s["name"], "last_modified": s["last_modified"], "days": s["days_since_update"]}
            for s in sorted(outdated_skills, key=lambda x: -x["days_since_update"])[:10]
        ],
        "by_category": {cat: len(skills) for cat, skills in sorted(by_category.items(), key=lambda x: -len(x[1]))}
    }


# ============================================================================
# 3. Git 活动分析（纯文件检查，无 subprocess）
# ============================================================================

def analyze_git_activity():
    """检查 .git 目录是否存在，但不执行 git 命令"""
    results = {}
    projects = {
        "hermes": HERMES_HOME,
        "agent_evolution": Path(os.path.expanduser("~/projects/agent-evolution")),
    }

    for name, repo_dir in projects.items():
        git_dir = repo_dir / ".git"
        if git_dir.exists():
            try:
                # 扫描 .git/objects/ 下最新文件的修改时间（比 HEAD mtime 准确）
                objects_dir = git_dir / "objects"
                last_mtime = None
                if objects_dir.exists():
                    for root, dirs, files in os.walk(objects_dir):
                        for f in files:
                            fp = os.path.join(root, f)
                            fm = os.path.getmtime(fp)
                            if last_mtime is None or fm > last_mtime:
                                last_mtime = fm
                if last_mtime is not None:
                    mtime_dt = datetime.fromtimestamp(last_mtime)
                    days_ago = (now - mtime_dt).days
                    results[name] = {
                        "has_git": True,
                        "last_git_activity": mtime_dt.strftime("%Y-%m-%d"),
                        "days_since_last_git_activity": days_ago,
                        "activity_level": "active" if days_ago <= 7 else ("low" if days_ago <= 30 else "inactive"),
                        "note": "基于 .git/objects/ 最新文件修改时间判断（无 git 命令调用）"
                    }
                else:
                    results[name] = {"has_git": True, "note": ".git/objects/ 为空"}
            except Exception as e:
                results[name] = {"has_git": True, "note": f"检查失败: {str(e)}"}
        else:
            results[name] = {"has_git": False, "note": "无 .git 目录"}

    return results


# ============================================================================
# 4. 改进计划生成
# ============================================================================

def generate_plan(cron_health, skills_audit, git_activity):
    actions = []

    # Cron 任务相关
    if "error" not in cron_health:
        for job_id, job_data in cron_health.get("jobs", {}).items():
            status = job_data.get("status", "unknown")
            if status == "failing":
                actions.append({
                    "id": f"cron-fail-{job_id}",
                    "type": "cron_failure",
                    "priority": "P1",
                    "title": f"Cron 任务 {job_id} 频繁失败",
                    "description": f"成功率: {job_data.get('success_rate', 0)*100:.0f}%",
                    "execution": "auto",
                    "steps": [
                        f"自动重启 cron 任务 {job_id}",
                        "监控后续运行状态"
                    ],
                    "auto_fix": {"type": "restart_cron", "job_id": job_id}
                })
            if job_data.get("error_patterns"):
                for err in job_data["error_patterns"][:2]:
                    actions.append({
                        "id": f"cron-err-{job_id}",
                        "type": "cron_error_pattern",
                        "priority": "P2",
                        "title": f"重复错误模式: {job_id}",
                        "description": f"出现 {err['count']} 次",
                        "execution": "review",
                        "steps": ["分析错误根因", "实施修复"]
                    })

    # 技能库相关 — ★ 只对真实的技能（非 curator_backups 等）标记 auto
    if "error" not in skills_audit:
        missing = skills_audit.get("missing_docs", [])
        if missing:
            actions.append({
                "id": "skill-missing-docs",
                "type": "skill_documentation",
                "priority": "P2",
                "title": f"{len(missing)} 个技能缺少 SKILL.md",
                "description": f"缺失: {', '.join(s['name'] for s in missing[:5])}",
                "execution": "auto",
                "steps": ["为缺失技能创建基础 SKILL.md"],
                "auto_fix": {"type": "create_skill_docs", "skills": missing}
            })

        empty = skills_audit.get("empty_skills", [])
        if empty:
            actions.append({
                "id": "skill-empty-docs",
                "type": "skill_content",
                "priority": "P2",
                "title": f"{len(empty)} 个技能文档内容过短",
                "description": f"需要充实: {', '.join(s['name'] for s in empty[:5])}",
                "execution": "review",
                "steps": ["审查并充实技能文档"]
            })

        outdated = skills_audit.get("outdated_skills", [])
        if outdated:
            actions.append({
                "id": "skill-outdated",
                "type": "skill_updates",
                "priority": "P3",
                "title": f"{len(outdated)} 个技能超过 30 天未更新",
                "description": f"最旧: {outdated[0]['name']} ({outdated[0]['days']} 天)",
                "execution": "discuss",
                "steps": ["评估是否需要更新"]
            })

    # Git 活动相关
    for project, data in git_activity.items():
        if data.get("activity_level") == "inactive":
            actions.append({
                "id": f"git-inactive-{project}",
                "type": "project_activity",
                "priority": "P3",
                "title": f"{project} 项目近一周无 Git 活动",
                "description": f"距上次活动: {data.get('days_since_last_git_activity', '?')} 天",
                "execution": "discuss",
                "steps": ["确认项目是否活跃"]
            })

    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    actions.sort(key=lambda a: priority_order.get(a.get("priority", "P3"), 3))

    return {
        "timestamp": now.isoformat(),
        "total_actions": len(actions),
        "auto_executable": sum(1 for a in actions if a["execution"] == "auto"),
        "needs_review": sum(1 for a in actions if a["execution"] == "review"),
        "for_discussion": sum(1 for a in actions if a["execution"] == "discuss"),
        "actions": actions
    }


# ============================================================================
# 5. 自动修复执行器（新模块）
# ============================================================================

class EvolutionExecutor:
    """
    分析后的自动执行阶段。
    只运行标记为 "execution": "auto" 的改进项。
    """
    def __init__(self):
        self.results = []

    def execute(self, plan):
        if not plan or not plan.get("actions"):
            return {"executed": 0, "results": []}

        for action in plan["actions"]:
            if action.get("execution") != "auto":
                continue

            action_type = action.get("type", "")
            auto_fix = action.get("auto_fix", {})

            if action_type == "skill_documentation" and auto_fix.get("type") == "create_skill_docs":
                self._create_missing_skill_docs(auto_fix.get("skills", []))
            elif action_type == "cron_failure" and auto_fix.get("type") == "restart_cron":
                self._schedule_cron_restart(auto_fix.get("job_id", ""))

        return {
            "timestamp": now.isoformat(),
            "executed": len(self.results),
            "results": self.results
        }

    def _create_missing_skill_docs(self, skills):
        for skill in skills:
            name = skill["name"]
            parts = name.split("/")
            if len(parts) == 2:
                category, skill_name = parts
            else:
                category = "general"
                skill_name = name

            skill_path = SKILLS_DIR / category / skill_name
            skill_md = skill_path / "SKILL.md"

            if not skill_path.exists() or skill_md.exists():
                self.results.append({
                    "skill": name,
                    "action": "create_skill_md",
                    "status": "skipped",
                    "reason": "目录不存在或文件已存在"
                })
                continue

            try:
                content = f"""---
name: {skill_name}
description: TODO: 补充技能描述
category: {category}
---

# {skill_name}

## 概述

TODO: 补充技能说明

## 使用方法

TODO: 补充使用方法

## 注意事项

- 待补充
"""
                skill_md.write_text(content, encoding="utf-8")
                self.results.append({
                    "skill": name,
                    "action": "create_skill_md",
                    "path": str(skill_md),
                    "status": "success"
                })
                print(f"  ✅ 已创建 SKILL.md: {skill_md}")
            except Exception as e:
                self.results.append({
                    "skill": name,
                    "action": "create_skill_md",
                    "status": "error",
                    "error": str(e)
                })
                print(f"  ❌ 创建失败 {name}: {e}")

    def _schedule_cron_restart(self, job_id):
        """写入 cron 重启指令供 MCP server / cron supervisor 消费"""
        if not job_id:
            return

        instruction = {
            "type": "cron_restart",
            "job_id": job_id,
            "timestamp": now.isoformat(),
            "reason": "自动检测到频繁失败，触发重启"
        }

        fix_dir = EVOLUTION_DIR / "fix_instructions"
        fix_dir.mkdir(parents=True, exist_ok=True)

        instruction_file = fix_dir / f"restart-cron-{job_id}-{today_str}.json"
        try:
            instruction_file.write_text(json.dumps(instruction, ensure_ascii=False, indent=2), encoding="utf-8")
            self.results.append({
                "action": "schedule_cron_restart",
                "job_id": job_id,
                "instruction_file": str(instruction_file),
                "status": "scheduled"
            })
            print(f"  📋 已生成 cron 重启指令: {instruction_file}")
        except Exception as e:
            self.results.append({
                "action": "schedule_cron_restart",
                "job_id": job_id,
                "status": "error",
                "error": str(e)
            })


# ============================================================================
# 6. GEP 信号桥接（新模块）
# ============================================================================

def emit_gep_signals(plan, execution_results):
    """
    将分析结果转化为 GEP 引擎可消费的信号文件。
    GEP 的 signals.js 会读取这些文件作为进化信号。
    """
    signals = []

    # 从改进计划中提取信号
    for action in plan.get("actions", []):
        p = action.get("priority", "P3")
        if p in ("P0", "P1"):
            signals.append("log_error")
        if action.get("type") == "cron_failure":
            signals.append("recurring_error")
        if action.get("type") == "skill_documentation":
            signals.append("capability_gap")
        if action.get("type") == "skill_content":
            signals.append("user_improvement_suggestion")

    # 从执行结果中提取信号
    if execution_results.get("executed", 0) > 0:
        signals.append("stable_success_plateau")

    if not signals:
        signals.append("stable_success_plateau")

    signal_data = {
        "timestamp": now.isoformat(),
        "source": "agent_evolution_v2_daily_analysis",
        "signals": list(set(signals)),
        "plan": {
            "total_actions": plan.get("total_actions", 0),
            "auto_executed": execution_results.get("executed", 0)
        }
    }

    signal_file = EVOLUTION_DIR / f"gep-signals-{today_str}.json"
    signal_file.write_text(json.dumps(signal_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  📡 GEP 信号已生成: {signal_file} ({len(signals)} 个信号)")
    return signal_data


# ============================================================================
# 7. 报告生成
# ============================================================================

def generate_report(cron_health, skills_audit, git_activity, plan, execution_results=None):
    report = f"""# Agent Evolution v2 — 每日分析报告

**生成时间**: {now_str}
**系统**: Hermes Agent (自我分析)
**分析方式**: 纯 Python 分析（无 subprocess/git 命令）

---

## 📊 系统概览

### 🔧 Cron 任务健康

"""
    if "error" not in cron_health:
        report += f"| 状态 | 数量 |\n|------|------|\n"
        report += f"| ✅ 健康 | {cron_health.get('healthy', 0)} |\n"
        report += f"| ⚠️ 降级 | {cron_health.get('degraded', 0)} |\n"
        report += f"| ❌ 异常 | {cron_health.get('failing', 0)} |\n\n"
        report += f"**总任务数**: {cron_health.get('total_jobs', 0)}\n\n"

        for job_id, job_data in cron_health.get("jobs", {}).items():
            status = job_data.get("status", "unknown")
            if status in ("degraded", "failing"):
                report += f"- **{job_id}** ({status}): 成功率 {job_data.get('success_rate', 0)*100:.0f}%\n"
            elif status == "unknown":
                report += f"- **{job_id}** ({status}): {job_data.get('reason', '未知')}\n"

        if not any(j.get("status") in ("degraded", "failing", "unknown") for j in cron_health.get("jobs", {}).values()):
            report += "✅ 所有 Cron 任务运行正常\n"
    else:
        report += f"⚠️ 无法获取 Cron 任务数据: {cron_health.get('error', '未知错误')}\n"

    report += "\n### 📚 技能库质量\n\n"
    if "error" not in skills_audit:
        report += f"| 指标 | 数值 |\n|------|------|\n"
        report += f"| 总技能数 | {skills_audit['total_skills']} |\n"
        report += f"| 有文档 | {skills_audit['with_documentation']} |\n"
        report += f"| 缺文档 | {skills_audit['without_documentation']} |\n"
        report += f"| 内容过短 | {len(skills_audit.get('empty_skills', []))} |\n"
        report += f"| 超过 30 天未更新 | {len(skills_audit.get('outdated_skills', []))} |\n"

        missing = skills_audit.get("missing_docs", [])
        if missing:
            report += "\n**缺文档的技能**:\n"
            for s in missing:
                report += f"- {s['name']}\n"

        outdated = skills_audit.get("outdated_skills", [])
        if outdated:
            report += "\n**最旧技能**:\n"
            for s in outdated[:5]:
                report += f"- {s['name']}: {s['days']} 天未更新\n"
    else:
        report += f"⚠️ 无法获取技能库数据: {skills_audit.get('error', '未知错误')}\n"

    report += "\n### 📝 项目活动\n\n"
    if git_activity:
        for project, data in git_activity.items():
            if data.get("has_git"):
                level = data.get("activity_level", "unknown")
                emoji = {"active": "✅", "low": "⚠️", "inactive": "❌"}.get(level, "❓")
                report += f"{emoji} **{project}**: 活动状态 {level}"
                if "days_since_last_git_activity" in data:
                    report += f" (距上次 {data['days_since_last_git_activity']} 天)"
                report += f"\n"
            else:
                report += f"⚠️ **{project}**: {data.get('note', '无 .git 目录')}\n"
    else:
        report += "⚠️ 无法获取项目数据\n"

    report += f"""

---

## 🎯 改进计划

**总计**: {plan.get('total_actions', 0)} 项
- 🤖 可自动执行: {plan.get('auto_executable', 0)} 项
- 👀 需人工审核: {plan.get('needs_review', 0)} 项
- 💬 需讨论: {plan.get('for_discussion', 0)} 项

"""

    for action in plan.get("actions", []):
        emoji = {"P0": "🚨", "P1": "🔴", "P2": "🟡", "P3": "🔵"}.get(action["priority"], "⚪")
        exec_emoji = {"auto": "🤖", "review": "👀", "discuss": "💬"}.get(action.get("execution", ""), "❓")
        report += f"### {emoji} [{action['priority']}] {action['title']} {exec_emoji}\n\n"
        report += f"{action.get('description', '')}\n\n"
        if action.get("steps"):
            report += "**执行步骤**:\n"
            for i, step in enumerate(action["steps"], 1):
                report += f"{i}. {step}\n"
            report += "\n"

    if not plan.get("actions"):
        report += "✅ 无需改进，系统状态良好\n"

    # ★ 新：自动执行结果
    if execution_results and execution_results.get("executed", 0) > 0:
        report += f"""

---

## ✅ 自动执行结果

本次自动执行了 {execution_results['executed']} 项改进：

"""
        for r in execution_results.get("results", []):
            status_emoji = {"success": "✅", "skipped": "⏭️", "error": "❌", "scheduled": "📋"}.get(r.get("status", ""), "❓")
            skill_name = r.get("skill", r.get("job_id", r.get("action", "未知")))
            report += f"- {status_emoji} **{skill_name}**: {r.get('action', '')} — {r.get('status', '')}\n"

    report += f"""

---

## 📋 总结

1. **系统整体健康状况**: 见上方概览
2. **具体问题**: 见改进计划
3. **自动执行操作**: {"已完成 " + str(execution_results.get('executed', 0)) + " 项改进" if execution_results and execution_results.get('executed', 0) > 0 else "无自动执行项"}
4. **需人工处理**: 见改进计划中"需人工审核"和"需讨论"项

---

*Agent Evolution v2 — Hermes 自我分析 | 数据来源: Hermes 自身系统*
"""
    return report


# ============================================================================
# 主流程
# ============================================================================

def main(execute_fixes=True):
    print("=" * 60)
    print("🧬 Agent Evolution v2 — 每日分析（含自动执行）")
    print("=" * 60)

    # 1. Cron 健康
    print("\n📊 分析 Cron 任务健康...")
    cron_health = analyze_cron_health()
    if "error" in cron_health:
        print(f"  ⚠️ {cron_health['error']}")
    else:
        print(f"  总任务: {cron_health['total_jobs']}, 健康: {cron_health['healthy']}, "
              f"降级: {cron_health['degraded']}, 异常: {cron_health['failing']}")

    # 2. 技能审计
    print("\n📚 审计技能库质量...")
    skills_audit = analyze_skills()
    if "error" in skills_audit:
        print(f"  ⚠️ {skills_audit['error']}")
    else:
        print(f"  总技能: {skills_audit['total_skills']}, 有文档: {skills_audit['with_documentation']}, "
              f"缺文档: {skills_audit['without_documentation']}")

    # 3. Git 活动
    print("\n📝 检查项目活动...")
    git_activity = analyze_git_activity()
    for project, data in git_activity.items():
        print(f"  {project}: {data.get('note', data.get('activity_level', 'unknown'))}")

    # 4. 生成改进计划
    print("\n🎯 生成改进计划...")
    plan = generate_plan(cron_health, skills_audit, git_activity)
    print(f"  改进项: {plan['total_actions']} (自动: {plan['auto_executable']}, "
          f"待审: {plan['needs_review']}, 讨论: {plan['for_discussion']})")

    # ★ 5. 执行自动修复（核心新增！）
    execution_results = {"executed": 0, "results": []}
    if execute_fixes and plan.get("auto_executable", 0) > 0:
        print("\n🤖 执行自动改进...")
        executor = EvolutionExecutor()
        execution_results = executor.execute(plan)
        print(f"  已执行: {execution_results['executed']} 项")
        for r in execution_results.get("results", []):
            status_emoji = {"success": "✅", "skipped": "⏭️", "error": "❌", "scheduled": "📋"}.get(r.get("status", ""), "❓")
            print(f"    {status_emoji} {r.get('skill', r.get('job_id', r.get('action', '?')))}: {r.get('status', '')}")
    elif execute_fixes:
        print("\n🤖 自动改进: 无可执行项，跳过")

    # ★ 6. 生成 GEP 信号（新！）
    print("\n📡 生成 GEP 进化信号...")
    signal_data = emit_gep_signals(plan, execution_results)
    print(f"  信号: {len(signal_data.get('signals', []))} 个")

    # 7. 生成报告
    print("\n📄 生成报告...")
    report = generate_report(cron_health, skills_audit, git_activity, plan, execution_results)

    # 8. 保存文件
    report_file = EVOLUTION_DIR / f"evolution-report-{today_str}.md"
    report_file.write_text(report, encoding="utf-8")

    plan_file = EVOLUTION_DIR / f"evolution-plan-{today_str}.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    data_file = EVOLUTION_DIR / f"evolution-data-{today_str}.json"
    data_file.write_text(json.dumps({
        "cron_health": cron_health,
        "skills_audit": skills_audit,
        "git_activity": git_activity,
        "execution_results": execution_results,
        "gep_signals": signal_data
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ 报告已保存: {report_file}")
    print(f"✅ 计划已保存: {plan_file}")
    print(f"✅ 数据已保存: {data_file}")
    print(f"\n{'='*60}")
    print(f"✅ 分析完成 — 自动执行: {execution_results['executed']} 项")
    print(f"{'='*60}")

    return {
        "cron_health": cron_health,
        "skills_audit": skills_audit,
        "git_activity": git_activity,
        "plan": plan,
        "execution_results": execution_results,
        "gep_signals": signal_data,
        "report_file": str(report_file)
    }


if __name__ == "__main__":
    result = main()
