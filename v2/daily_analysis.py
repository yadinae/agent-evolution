#!/usr/bin/env python3
"""
Agent Evolution v2 每日分析 — 纯 Python 实现（无 subprocess）
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
            # 检查最近的修改时间
            try:
                # 检查 HEAD 文件的修改时间作为近似
                head_file = git_dir / "HEAD"
                if head_file.exists():
                    mtime = datetime.fromtimestamp(head_file.stat().st_mtime)
                    days_ago = (now - mtime).days
                    results[name] = {
                        "has_git": True,
                        "last_git_activity": mtime.strftime("%Y-%m-%d"),
                        "days_since_last_git_activity": days_ago,
                        "activity_level": "active" if days_ago <= 7 else ("low" if days_ago <= 30 else "inactive"),
                        "note": "无 git 命令，仅基于 .git 目录修改时间判断"
                    }
                else:
                    results[name] = {"has_git": True, "note": "无法读取 .git/HEAD"}
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
                    "execution": "review",
                    "steps": [
                        f"检查 ~/.hermes/cron/output/{job_id}/ 中的错误",
                        "分析最近失败原因",
                        "修复或调整任务配置"
                    ]
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

    # 技能库相关
    if "error" not in skills_audit:
        missing = skills_audit.get("missing_docs", [])
        if missing:
            actions.append({
                "id": "skill-missing-docs",
                "type": "skill_documentation",
                "priority": "P2",
                "title": f"{len(missing)} 个技能缺少 SKILL.md",
                "description": f"缺失: {', '.join(s['name'] for s in missing[:5])}",
                "execution": "review",
                "steps": ["为缺失技能创建基础 SKILL.md"]
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
# 5. 报告生成
# ============================================================================

def generate_report(cron_health, skills_audit, git_activity, plan):
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

    report += f"""
---

## 📋 总结

1. **系统整体健康状况**: 见上方概览
2. **具体问题**: 见改进计划
3. **自动执行操作**: 本次为只读分析，未执行自动修复
4. **需人工处理**: 见改进计划中"需人工审核"和"需讨论"项

---

*Agent Evolution v2 — Hermes 自我分析 | 数据来源: Hermes 自身系统*
"""
    return report


# ============================================================================
# 主流程
# ============================================================================

def main():
    print("=" * 60)
    print("🧬 Agent Evolution v2 — 每日分析（纯 Python）")
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
    print(f"  改进项: {plan['total_actions']}")

    # 5. 生成报告
    print("\n📄 生成报告...")
    report = generate_report(cron_health, skills_audit, git_activity, plan)

    # 6. 保存文件
    report_file = EVOLUTION_DIR / f"evolution-report-{today_str}.md"
    report_file.write_text(report, encoding="utf-8")

    plan_file = EVOLUTION_DIR / f"evolution-plan-{today_str}.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")

    data_file = EVOLUTION_DIR / f"evolution-data-{today_str}.json"
    data_file.write_text(json.dumps({
        "cron_health": cron_health,
        "skills_audit": skills_audit,
        "git_activity": git_activity
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ 报告已保存: {report_file}")
    print(f"✅ 计划已保存: {plan_file}")
    print(f"✅ 数据已保存: {data_file}")
    print(f"\n{'='*60}")
    print("✅ 分析完成")
    print(f"{'='*60}")

    return {
        "cron_health": cron_health,
        "skills_audit": skills_audit,
        "git_activity": git_activity,
        "plan": plan,
        "report_file": str(report_file)
    }


if __name__ == "__main__":
    result = main()
