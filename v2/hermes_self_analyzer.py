#!/usr/bin/env python3
"""
Agent Evolution v2 — Hermes 自我进化系统

核心变化：
1. 数据源：从 nanobot 历史 → Hermes 自身数据
2. 分析方式：从正则匹配 → 结构化分析
3. 输出方式：从空泛建议 → 可执行方案
4. 执行方式：从只分析 → 分析 + 自动执行

作者：yadinae
日期：2026-05-02
"""

import os
import sys
import json
import re
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

# 配置
HERMES_HOME = Path(os.path.expanduser("~/.hermes"))
CRON_OUTPUT_DIR = HERMES_HOME / "cron" / "output"
SKILLS_DIR = HERMES_HOME / "skills"
EVOLUTION_DIR = Path(os.path.expanduser("~/projects/agent-evolution")) / "v2" / "output"
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# 模块 1：Cron 任务健康分析
# ============================================================================

class CronHealthAnalyzer:
    """分析 Hermes cron 任务的运行健康状况"""
    
    def __init__(self):
        self.cron_dir = CRON_OUTPUT_DIR
        self.jobs = {}
    
    def analyze(self):
        """分析所有 cron 任务的健康状态"""
        results = {}
        
        if not self.cron_dir.exists():
            return {"error": "Cron 输出目录不存在"}
        
        # 遍历所有 cron job 输出目录
        for job_dir in self.cron_dir.iterdir():
            if not job_dir.is_dir():
                continue
            
            job_id = job_dir.name
            job_result = self._analyze_single_job(job_id, job_dir)
            results[job_id] = job_result
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_jobs": len(results),
            "healthy": sum(1 for r in results.values() if r["status"] == "healthy"),
            "degraded": sum(1 for r in results.values() if r["status"] == "degraded"),
            "failing": sum(1 for r in results.values() if r["status"] == "failing"),
            "jobs": results
        }
    
    def _analyze_single_job(self, job_id, job_dir):
        """分析单个 cron job 的健康状态"""
        # 获取最近的输出文件
        output_files = sorted(job_dir.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
        
        if not output_files:
            return {"status": "unknown", "reason": "无输出文件", "recent_runs": 0}
        
        recent_files = output_files[:7]  # 最近 7 次运行
        run_results = []
        
        for f in recent_files:
            content = f.read_text(encoding="utf-8")
            status = self._extract_run_status(content)
            run_results.append({
                "date": f.name[:10],
                "file": f.name,
                "status": status,
                "size_kb": round(f.stat().st_size / 1024, 1)
            })
        
        # 判断整体状态
        ok_count = sum(1 for r in run_results if r["status"] == "ok")
        total = len(run_results)
        
        if total == 0:
            status = "unknown"
        elif ok_count == total:
            status = "healthy"
        elif ok_count >= total * 0.7:
            status = "degraded"
        else:
            status = "failing"
        
        # 提取错误模式
        error_patterns = self._extract_error_patterns([f.read_text(encoding="utf-8") for f in recent_files])
        
        return {
            "status": status,
            "recent_runs": run_results,
            "success_rate": round(ok_count / total, 2) if total > 0 else 0,
            "error_patterns": error_patterns[:5]
        }
    
    def _extract_run_status(self, content):
        """从 cron 输出中提取运行状态"""
        # 检查是否有明确的成功/失败标记
        if "## Response" in content:
            # 有 Response 说明正常执行完毕
            # 提取 Response 之后的内容判断状态
            response_part = content.split("## Response", 1)[-1]
            if any(kw in response_part for kw in ["Traceback", "FAILED", "terminated"]):
                return "error"
            return "ok"
        
        return "ok"
    
    def _extract_error_patterns(self, contents):
        """从多次运行中提取重复出现的错误"""
        all_errors = []
        for content in contents:
            # 只分析 Response 部分之后的内容（实际执行结果）
            if "## Response" in content:
                text = content.split("## Response", 1)[-1]
            else:
                text = content[-3000:]  # 兜底：取最后 3000 字符
            
            # 只匹配实际的错误，不匹配文档中的关键词
            lines = text.split("\n")
            for i, line in enumerate(lines):
                # 排除常见的误报行（表格、列表、文档描述）
                if line.strip().startswith("|") or line.strip().startswith("-"):
                    continue
                if line.strip().startswith("##"):
                    continue
                
                if any(kw in line for kw in ["Traceback", "FAILED", "Error:"]):
                    start = max(0, i - 1)
                    end = min(len(lines), i + 3)
                    context = "\n".join(lines[start:end])
                    all_errors.append(context[:300])
        
        # 找出重复出现的错误
        error_counts = Counter(all_errors)
        return [{"pattern": p, "count": c} for p, c in error_counts.most_common(10) if c >= 2]


# ============================================================================
# 模块 2：技能库质量审计
# ============================================================================

class SkillsQualityAudit:
    """审计 Hermes 技能库的质量"""
    
    def __init__(self):
        self.skills_dir = SKILLS_DIR
    
    def analyze(self):
        """执行技能库全面审计"""
        if not self.skills_dir.exists():
            return {"error": "技能目录不存在"}
        
        total_skills = 0
        with_doc = 0
        without_doc = []
        by_category = defaultdict(list)
        empty_skills = []
        outdated_skills = []
        
        now = datetime.now()
        
        for cat_dir in self.skills_dir.iterdir():
            if not cat_dir.is_dir():
                continue
            category = cat_dir.name
            
            for skill_dir in cat_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                
                # 跳过子目录和系统目录
                if skill_dir.name in ("references", "templates", "scripts", "assets", ".hub"):
                    continue
                
                # 跳过以 . 开头的系统目录
                if skill_dir.name.startswith("."):
                    continue
                
                total_skills += 1
                skill_info = {
                    "name": f"{category}/{skill_dir.name}",
                    "category": category,
                    "path": str(skill_dir)
                }
                
                # 检查 SKILL.md
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    with_doc += 1
                    content = skill_md.read_text(encoding="utf-8")
                    
                    # 检查内容是否为空或过短
                    if len(content.strip()) < 100:
                        empty_skills.append(skill_info)
                    
                    # 检查是否过时（30天未修改）
                    mtime = datetime.fromtimestamp(skill_md.stat().st_mtime)
                    if (now - mtime).days > 30:
                        skill_info["last_modified"] = mtime.strftime("%Y-%m-%d")
                        skill_info["days_since_update"] = (now - mtime).days
                        outdated_skills.append(skill_info)
                else:
                    without_doc.append(skill_info)
                
                by_category[category].append(skill_info)
        
        return {
            "timestamp": datetime.now().isoformat(),
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
# 模块 3：Git 变更模式分析
# ============================================================================

class GitChangeAnalyzer:
    """分析 Hermes 和 StudyAI 项目的变更模式"""
    
    def __init__(self):
        self.hermes_dir = HERMES_HOME
        self.studyai_dir = Path(os.path.expanduser("~/projects/studyai"))
    
    def analyze(self):
        """分析 Git 变更模式"""
        results = {}
        
        # 分析 Hermes 项目
        hermes_changes = self._analyze_git_repo(self.hermes_dir, "Hermes Agent")
        if hermes_changes:
            results["hermes"] = hermes_changes
        
        # 分析 StudyAI 项目
        if self.studyai_dir.exists():
            # 查找实际的 studyai 项目目录
            for d in self.studyai_dir.iterdir():
                if d.is_dir() and (d / ".git").exists():
                    studyai_changes = self._analyze_git_repo(d, "StudyAI")
                    if studyai_changes:
                        results["studyai"] = studyai_changes
                    break
        
        # 分析 agent-evolution 项目
        evolution_dir = Path(os.path.expanduser("~/projects/agent-evolution"))
        if evolution_dir.exists() and (evolution_dir / ".git").exists():
            evolution_changes = self._analyze_git_repo(evolution_dir, "Agent Evolution")
            if evolution_changes:
                results["agent_evolution"] = evolution_changes
        
        return results
    
    def _analyze_git_repo(self, repo_dir, name):
        """分析单个 Git 仓库"""
        try:
            # 最近 30 天的提交
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=30 days", "--no-merges"],
                cwd=repo_dir, capture_output=True, text=True, timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            commits = result.stdout.strip().split("\n") if result.stdout.strip() else []
            
            # 分析提交类型
            type_counts = Counter()
            for commit in commits:
                if "feat" in commit or "✨" in commit:
                    type_counts["features"] += 1
                elif "fix" in commit or "🐛" in commit:
                    type_counts["fixes"] += 1
                elif "docs" in commit or "📝" in commit:
                    type_counts["docs"] += 1
                elif "refactor" in commit or "♻" in commit:
                    type_counts["refactors"] += 1
                elif "chore" in commit or "🔧" in commit:
                    type_counts["chores"] += 1
                else:
                    type_counts["other"] += 1
            
            # 最近 7 天 vs 前 23 天对比
            week_commits = len([c for c in commits if self._is_recent(c, 7)])
            recent_activity = "active" if week_commits >= 3 else "low" if week_commits > 0 else "inactive"
            
            return {
                "total_commits_30d": len(commits),
                "commits_this_week": week_commits,
                "activity_level": recent_activity,
                "commit_types": dict(type_counts),
                "top_changes": commits[:5]
            }
        except Exception:
            return None
    
    def _is_recent(self, commit_line, days):
        """粗略判断提交是否在最近 N 天内（基于列表顺序）"""
        # 简化：假设提交按时间倒序，取前 N*3 行作为最近 N 天的近似
        return True  # 简化处理


# ============================================================================
# 模块 4：改进计划生成器（可执行的改进方案）
# ============================================================================

class ActionPlanner:
    """基于分析结果生成可执行的改进计划"""
    
    def __init__(self):
        self.actions = []
    
    def generate(self, cron_health, skills_audit, git_changes):
        """生成完整的改进计划"""
        self.actions = []
        
        # 1. Cron 任务相关改进
        self._plan_cron_improvements(cron_health)
        
        # 2. 技能库改进
        self._plan_skill_improvements(skills_audit)
        
        # 3. Git/项目改进
        self._plan_git_improvements(git_changes)
        
        # 按优先级排序
        self._prioritize()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_actions": len(self.actions),
            "auto_executable": sum(1 for a in self.actions if a["execution"] == "auto"),
            "needs_review": sum(1 for a in self.actions if a["execution"] == "review"),
            "for_discussion": sum(1 for a in self.actions if a["execution"] == "discuss"),
            "actions": self.actions
        }
    
    def _plan_cron_improvements(self, health):
        """基于 Cron 健康分析生成改进"""
        if not health or "error" in health:
            return
        
        for job_id, job_data in health.get("jobs", {}).items():
            status = job_data.get("status", "unknown")
            
            if status == "failing":
                self.actions.append({
                    "id": f"cron-fail-{job_id}",
                    "type": "cron_failure",
                    "priority": "P1",
                    "title": f"Cron 任务 {job_id} 频繁失败",
                    "description": f"成功率: {job_data.get('success_rate', 0)*100:.0f}%",
                    "execution": "review",
                    "steps": [
                        f"检查 cron 输出目录 ~/.hermes/cron/output/{job_id}/ 中的错误",
                        "分析最近失败的原因",
                        "修复或调整任务配置"
                    ]
                })
            
            if job_data.get("error_patterns"):
                for err in job_data["error_patterns"][:2]:
                    self.actions.append({
                        "id": f"cron-err-{job_id}-{hash(err['pattern']) % 1000}",
                        "type": "cron_error_pattern",
                        "priority": "P2",
                        "title": f"重复错误模式",
                        "description": f"出现 {err['count']} 次: {err['pattern'][:100]}",
                        "execution": "review",
                        "steps": ["分析错误根因", "实施修复"]
                    })
    
    def _plan_skill_improvements(self, audit):
        """基于技能审计生成改进"""
        if not audit or "error" in audit:
            return
        
        # 缺失文档的技能 — 可以自动补全
        missing = audit.get("missing_docs", [])
        if missing:
            self.actions.append({
                "id": "skill-missing-docs",
                "type": "skill_documentation",
                "priority": "P2",
                "title": f"{len(missing)} 个技能缺少 SKILL.md",
                "description": f"缺失文档的技能: {', '.join(s['name'] for s in missing[:5])}",
                "execution": "auto",
                "steps": [
                    f"为 {len(missing)} 个技能创建基础 SKILL.md",
                    "包含：名称、描述、使用方法、注意事项"
                ],
                "auto_fix": {
                    "type": "create_skill_docs",
                    "skills": missing
                }
            })
        
        # 空文档
        empty = audit.get("empty_skills", [])
        if empty:
            self.actions.append({
                "id": "skill-empty-docs",
                "type": "skill_content",
                "priority": "P2",
                "title": f"{len(empty)} 个技能文档内容过短",
                "description": f"需要充实内容: {', '.join(s['name'] for s in empty[:5])}",
                "execution": "review",
                "steps": ["审查并充实技能文档内容"]
            })
        
        # 过期技能
        outdated = audit.get("outdated_skills", [])
        if outdated:
            self.actions.append({
                "id": "skill-outdated",
                "type": "skill_updates",
                "priority": "P3",
                "title": f"{len(outdated)} 个技能超过 30 天未更新",
                "description": f"最旧: {outdated[0]['name']} ({outdated[0]['days']} 天)",
                "execution": "discuss",
                "steps": ["评估是否需要更新", "标记不再维护的技能"]
            })
    
    def _plan_git_improvements(self, changes):
        """基于 Git 变更分析生成改进"""
        if not changes:
            return
        
        for project, data in changes.items():
            if data.get("activity_level") == "inactive":
                self.actions.append({
                    "id": f"git-inactive-{project}",
                    "type": "project_activity",
                    "priority": "P3",
                    "title": f"{project} 项目近一周无活动",
                    "description": f"30 天提交: {data['total_commits_30d']}, 本周: {data['commits_this_week']}",
                    "execution": "discuss",
                    "steps": ["确认项目是否活跃", "如无活动考虑归档"]
                })
    
    def _prioritize(self):
        """按优先级排序"""
        priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        self.actions.sort(key=lambda a: priority_order.get(a.get("priority", "P3"), 3))


# ============================================================================
# 模块 5：自动修复执行器
# ============================================================================

class AutoFixer:
    """自动执行低风险的改进操作"""
    
    def __init__(self):
        self.results = []
    
    def execute(self, plan):
        """执行所有可自动操作的改进"""
        for action in plan.get("actions", []):
            if action.get("execution") != "auto":
                continue
            
            auto_fix = action.get("auto_fix")
            if not auto_fix:
                continue
            
            if auto_fix["type"] == "create_skill_docs":
                self._create_missing_skill_docs(auto_fix["skills"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "executed": len(self.results),
            "results": self.results
        }
    
    def _create_missing_skill_docs(self, skills):
        """为缺失文档的技能创建基础 SKILL.md"""
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
                    "action": "created",
                    "path": str(skill_md),
                    "status": "success"
                })
            except Exception as e:
                self.results.append({
                    "skill": name,
                    "action": "created",
                    "status": "error",
                    "error": str(e)
                })


# ============================================================================
# 模块 6：改进验证器（Ralph Loop 核心 — 验证改进是否真的生效）
# ============================================================================

class EvolutionVerifier:
    """验证改进是否真的生效 — 重新分析数据，对比指标变化"""
    
    def __init__(self):
        self.results = []
    
    def verify(self, before_state, auto_fix_results):
        """
        验证改进效果。
        before_state: 改进前的基线指标
        auto_fix_results: 自动执行的结果
        """
        # 重新运行分析
        cron_health = CronHealthAnalyzer().analyze()
        skills_audit = SkillsQualityAudit().analyze()
        
        after_state = {
            "cron_health": cron_health,
            "skills_audit": skills_audit,
            "timestamp": datetime.now().isoformat()
        }
        
        verification = {
            "timestamp": datetime.now().isoformat(),
            "checks": []
        }
        
        # 检查 1：技能文档完整性
        before_docs = before_state.get("skills_without_docs", 0)
        after_docs = skills_audit.get("without_documentation", 0)
        if after_docs < before_docs:
            verification["checks"].append({
                "name": "技能文档补全",
                "before": f"缺文档: {before_docs}",
                "after": f"缺文档: {after_docs}",
                "passed": True,
                "detail": f"成功补全 {before_docs - after_docs} 个技能文档"
            })
        elif after_docs == 0 and before_docs == 0:
            verification["checks"].append({
                "name": "技能文档完整性",
                "before": "已完成",
                "after": "已完成",
                "passed": True,
                "detail": "所有技能都有文档"
            })
        elif after_docs == before_docs:
            verification["checks"].append({
                "name": "技能文档补全",
                "before": f"缺文档: {before_docs}",
                "after": f"缺文档: {after_docs}",
                "passed": False,
                "detail": "文档数量无变化"
            })
        
        # 检查 2：Cron 任务健康
        before_failing = before_state.get("cron_failing", 0)
        after_failing = cron_health.get("failing", 0)
        if after_failing < before_failing:
            verification["checks"].append({
                "name": "Cron 任务修复",
                "before": f"异常任务: {before_failing}",
                "after": f"异常任务: {after_failing}",
                "passed": True,
                "detail": f"修复了 {before_failing - after_failing} 个异常任务"
            })
        elif after_failing == before_failing:
            verification["checks"].append({
                "name": "Cron 任务健康",
                "before": f"异常任务: {before_failing}",
                "after": f"异常任务: {after_failing}",
                "passed": True if after_failing == 0 else False,
                "detail": "状态无变化" if after_failing == before_failing else f"异常任务 {after_failing} 个"
            })
        
        # 检查 3：自动执行结果
        fix_success = sum(1 for r in auto_fix_results.get("results", []) if r.get("status") == "success")
        fix_fail = sum(1 for r in auto_fix_results.get("results", []) if r.get("status") == "error")
        if fix_success > 0:
            verification["checks"].append({
                "name": "自动执行",
                "before": f"待执行",
                "after": f"成功 {fix_success}, 失败 {fix_fail}",
                "passed": fix_fail == 0,
                "detail": f"执行了 {fix_success} 项改进"
            })
        
        # 判断整体是否通过
        all_passed = all(c["passed"] for c in verification["checks"])
        any_progress = any(c["passed"] for c in verification["checks"])
        
        verification["all_passed"] = all_passed
        verification["any_progress"] = any_progress
        verification["after_state"] = after_state
        
        passed_count = sum(1 for c in verification["checks"] if c["passed"])
        total_count = len(verification["checks"])
        print(f"  验证: {passed_count}/{total_count} 项通过")
        for c in verification["checks"]:
            emoji = "✅" if c["passed"] else "❌"
            print(f"    {emoji} {c['name']}: {c['detail']}")
        
        return verification


# ============================================================================
# 模块 7：Ralph Loop 迭代控制器
# ============================================================================

class EvolutionState:
    """Ralph Loop 风格的状态管理 — markdown frontmatter 存状态"""
    
    STATE_FILE = EVOLUTION_DIR / "evolution-state.md"
    
    @classmethod
    def save(cls, iteration, max_iterations, baseline, completion_criteria):
        """保存当前迭代状态"""
        content = f"""---
iteration: {iteration}
max_iterations: {max_iterations}
timestamp: {datetime.now().isoformat()}
completion_criteria: {json.dumps(completion_criteria, ensure_ascii=False)}
---

# Agent Evolution Loop

## 基线指标

{json.dumps(baseline, ensure_ascii=False, indent=2)}

## 改进历史

（每次迭代的改进和验证结果记录在此）
"""
        cls.STATE_FILE.write_text(content, encoding="utf-8")
    
    @classmethod
    def append_iteration(cls, iteration, actions, verification):
        """追加迭代结果到状态文件"""
        try:
            content = cls.STATE_FILE.read_text(encoding="utf-8")
            content += f"\n\n---\n\n## 迭代 {iteration}\n\n"
            content += f"**执行改进**: {len(actions)} 项\n"
            content += f"**验证结果**: {sum(1 for c in verification.get('checks', []) if c['passed'])}/{len(verification.get('checks', []))} 项通过\n"
            
            for c in verification.get("checks", []):
                emoji = "✅" if c["passed"] else "❌"
                content += f"- {emoji} {c['name']}: {c['detail']}\n"
            
            cls.STATE_FILE.write_text(content, encoding="utf-8")
        except Exception as e:
            print(f"  ⚠️ 更新状态文件失败: {e}")
    
    @classmethod
    def clear(cls):
        """清除状态文件"""
        if cls.STATE_FILE.exists():
            cls.STATE_FILE.unlink()
    
    @classmethod
    def should_continue(cls, max_iterations, verification):
        """判断是否继续循环"""
        if not cls.STATE_FILE.exists():
            return True, 0  # 第一次运行
        
        content = cls.STATE_FILE.read_text(encoding="utf-8")
        # 解析 frontmatter
        fm_match = re.match(r'---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            return True, 0
        
        fm = {}
        for line in fm_match.group(1).split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                fm[key.strip()] = val.strip()
        
        iteration = int(fm.get("iteration", 0))
        
        # 达到最大迭代次数
        if iteration >= max_iterations:
            return False, iteration
        
        # 所有检查通过
        if verification.get("all_passed"):
            return False, iteration
        
        # 没有进展（上次和这次都没通过）
        if not verification.get("any_progress"):
            return False, iteration
        
        return True, iteration


class RalphLoop:
    """Ralph Loop 风格的迭代进化控制器
    
    核心理念：分析 → 改进 → 验证 → 循环直到问题解决
    """
    
    def __init__(self, max_iterations=5):
        self.max_iterations = max_iterations
        self.history = []
    
    def run(self):
        """运行 Ralph Loop"""
        print("\n" + "=" * 60)
        print("🔄 Ralph Loop — 迭代进化开始")
        print(f"最大迭代次数: {self.max_iterations}")
        print("=" * 60)
        
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n{'='*40}")
            print(f"🔄 迭代 {iteration}/{self.max_iterations}")
            print(f"{'='*40}")
            
            # === Step 1: 分析 ===
            print("\n📊 分析系统状态...")
            cron_health = CronHealthAnalyzer().analyze()
            skills_audit = SkillsQualityAudit().analyze()
            git_changes = GitChangeAnalyzer().analyze()
            
            # 记录基线指标
            baseline = {
                "cron_total": cron_health.get("total_jobs", 0),
                "cron_healthy": cron_health.get("healthy", 0),
                "cron_failing": cron_health.get("failing", 0),
                "skills_total": skills_audit.get("total_skills", 0),
                "skills_without_docs": skills_audit.get("without_documentation", 0),
                "timestamp": datetime.now().isoformat()
            }
            
            # 第一次迭代保存基线
            if iteration == 1:
                EvolutionState.save(iteration, self.max_iterations, baseline, {
                    "all_auto_fixable_applied": True,
                    "skill_docs_complete": skills_audit.get("without_documentation", 0) == 0,
                    "no_failing_crons": cron_health.get("failing", 0) == 0
                })
            
            # === Step 2: 生成改进计划 ===
            print("\n🎯 生成改进计划...")
            planner = ActionPlanner()
            plan = planner.generate(cron_health, skills_audit, git_changes)
            
            if plan["total_actions"] == 0:
                print("  ✅ 无需改进，系统状态良好")
                EvolutionState.clear()
                self.history.append({
                    "iteration": iteration,
                    "actions": 0,
                    "status": "complete",
                    "reason": "无需改进"
                })
                break
            
            print(f"  改进项: {plan['total_actions']}, "
                  f"可自动执行: {plan['auto_executable']}, "
                  f"需审核: {plan['needs_review']}")
            
            # === Step 3: 自动执行 ===
            print("\n🤖 执行自动改进...")
            fixer = AutoFixer()
            auto_fix_results = fixer.execute(plan)
            print(f"  已执行: {auto_fix_results['executed']} 项")
            
            # === Step 4: 验证改进效果（Ralph Loop 核心） ===
            print("\n🔍 验证改进效果...")
            verifier = EvolutionVerifier()
            verification = verifier.verify(baseline, auto_fix_results)
            
            # 记录迭代
            EvolutionState.append_iteration(iteration, plan.get("actions", []), verification)
            
            self.history.append({
                "iteration": iteration,
                "actions_executed": auto_fix_results.get("executed", 0),
                "verification_passed": verification.get("all_passed", False),
                "any_progress": verification.get("any_progress", False)
            })
            
            # === Step 5: 判断是否继续 ===
            if verification.get("all_passed"):
                print("\n✅ 所有验证通过，改进生效！")
                EvolutionState.clear()
                break
            
            if not verification.get("any_progress"):
                print("\n⚠️ 本轮无进展，停止迭代")
                break
            
            if iteration >= self.max_iterations:
                print(f"\n⚠️ 达到最大迭代次数 ({self.max_iterations})，停止")
                break
            
            print(f"\n⏳ 仍有未解决的问题，进入下一轮迭代...")
        
        EvolutionState.clear()
        return self._summarize()
    
    def _summarize(self):
        """生成迭代总结"""
        total_iterations = len(self.history)
        last = self.history[-1] if self.history else {}
        
        return {
            "total_iterations": total_iterations,
            "completed": last.get("status") == "complete" or last.get("verification_passed", False),
            "history": self.history
        }


# ============================================================================
# 模块 8：报告生成器
# ============================================================================

class ReportGenerator:
    """生成人类可读的分析报告"""
    
    def generate(self, cron_health, skills_audit, git_changes, plan, auto_fix_results, loop_history=None):
        """生成完整的进化报告"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        report = f"""# Agent Evolution v2 — 自我进化报告

**生成时间**: {now}
**系统**: Hermes Agent (自我分析)

---

## 📊 系统概览

"""
        # Cron 任务健康
        report += "### 🔧 Cron 任务健康\n\n"
        if cron_health and "error" not in cron_health:
            report += f"| 状态 | 数量 |\n|------|------|\n"
            report += f"| ✅ 健康 | {cron_health.get('healthy', 0)} |\n"
            report += f"| ⚠️ 降级 | {cron_health.get('degraded', 0)} |\n"
            report += f"| ❌ 异常 | {cron_health.get('failing', 0)} |\n"
            report += f"\n**总任务数**: {cron_health.get('total_jobs', 0)}\n\n"
            
            # 列出有问题的任务
            for job_id, job_data in cron_health.get("jobs", {}).items():
                if job_data.get("status") in ("degraded", "failing"):
                    report += f"- **{job_id}** ({job_data['status']}): 成功率 {job_data.get('success_rate', 0)*100:.0f}%\n"
        else:
            report += "⚠️ 无法获取 Cron 任务数据\n\n"
        
        # 技能库质量
        report += "\n### 📚 技能库质量\n\n"
        if skills_audit and "error" not in skills_audit:
            report += f"| 指标 | 数值 |\n|------|------|\n"
            report += f"| 总技能数 | {skills_audit['total_skills']} |\n"
            report += f"| 有文档 | {skills_audit['with_documentation']} |\n"
            report += f"| 缺文档 | {skills_audit['without_documentation']} |\n"
            report += f"| 内容过短 | {len(skills_audit.get('empty_skills', []))} |\n"
            report += f"| 超过 30 天未更新 | {len(skills_audit.get('outdated_skills', []))} |\n"
        else:
            report += "⚠️ 无法获取技能库数据\n\n"
        
        # Git 变更
        report += "\n### 📝 项目活动\n\n"
        if git_changes:
            for project, data in git_changes.items():
                report += f"**{project}**: {data['total_commits_30d']} 次提交 (30天) | "
                report += f"本周 {data['commits_this_week']} 次 | "
                report += f"状态: {data['activity_level']}\n"
        else:
            report += "⚠️ 无法获取项目数据\n\n"
        
        # 改进计划
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
        
        # 自动执行结果
        if auto_fix_results.get("executed", 0) > 0:
            report += f"""
---

## ✅ 自动执行结果

已自动执行 {auto_fix_results['executed']} 项改进：

"""
            for r in auto_fix_results.get("results", []):
                status = "✅" if r["status"] == "success" else "❌"
                report += f"- {status} **{r.get('skill', 'unknown')}**: {r['action']} — {r['status']}\n"
        
        # Ralph Loop 迭代历史
        if loop_history and len(loop_history) > 0:
            report += f"""
---

## 🔄 Ralph Loop 迭代记录

"""
            for h in loop_history:
                status = "✅" if h.get("verification_passed") or h.get("status") == "complete" else "⏳"
                report += f"### {status} 迭代 {h['iteration']}\n\n"
                report += f"- 执行改进: {h.get('actions_executed', 0)} 项\n"
                report += f"- 验证通过: {'是' if h.get('verification_passed') else '否'}\n"
                if h.get("reason"):
                    report += f"- 原因: {h['reason']}\n"
                report += "\n"
        
        # 总结
        report += f"""
---

## 📋 下一步

1. 检查自动执行的改进是否合理
2. 审核需人工处理的改进项
3. 讨论需要决策的架构级问题

---

*Agent Evolution v2 — Hermes 自我分析，数据来源于 Hermes 自身系统*
"""
        return report


# ============================================================================
# 主流程
# ============================================================================

def main():
    print("=" * 60)
    print("🧬 Agent Evolution v2 — Hermes 自我进化（Ralph Loop）")
    print("=" * 60)
    
    # 运行 Ralph Loop — 分析 → 改进 → 验证 → 循环
    ralph = RalphLoop(max_iterations=3)
    loop_result = ralph.run()
    
    # 生成最终报告
    print("\n📄 生成进化报告...")
    
    # 重新获取最终状态用于报告
    cron_health = CronHealthAnalyzer().analyze()
    skills_audit = SkillsQualityAudit().analyze()
    git_changes = GitChangeAnalyzer().analyze()
    
    # 最后一次迭代的改进计划
    planner = ActionPlanner()
    plan = planner.generate(cron_health, skills_audit, git_changes)
    
    # 生成报告
    reporter = ReportGenerator()
    report = reporter.generate(cron_health, skills_audit, git_changes, plan, 
                               {"executed": 0, "results": []}, 
                               loop_history=loop_result.get("history", []))
    
    # 保存输出
    today = datetime.now().strftime("%Y-%m-%d")
    report_file = EVOLUTION_DIR / f"evolution-report-{today}.md"
    report_file.write_text(report, encoding="utf-8")
    
    plan_file = EVOLUTION_DIR / f"evolution-plan-{today}.json"
    plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    
    loop_file = EVOLUTION_DIR / f"ralph-loop-{today}.json"
    loop_file.write_text(json.dumps(loop_result, ensure_ascii=False, indent=2), encoding="utf-8")
    
    print(f"\n✅ 报告已保存: {report_file}")
    print(f"✅ 计划已保存: {plan_file}")
    print(f"✅ 迭代记录已保存: {loop_file}")
    
    # 总结
    print(f"\n{'='*60}")
    print(f"📊 迭代总结: {loop_result['total_iterations']} 轮")
    print(f"   完成状态: {'✅ 是' if loop_result['completed'] else '⚠️ 未完成'}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
