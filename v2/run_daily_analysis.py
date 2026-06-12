#!/usr/bin/env python3
"""Agent Evolution v2 Daily Analysis - Standalone Runner"""
import os, sys, json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict

HERMES_HOME = Path.home() / '.hermes'
CRON_OUTPUT_DIR = HERMES_HOME / 'cron' / 'output'
SKILLS_DIR = HERMES_HOME / 'skills'
EVOLUTION_DIR = Path.home() / 'projects' / 'agent-evolution' / 'v2' / 'output'
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

results = {}

# === Cron Health ===
cron_result = {}
if CRON_OUTPUT_DIR.exists():
    job_dirs = [d for d in CRON_OUTPUT_DIR.iterdir() if d.is_dir()]
    for job_dir in job_dirs:
        job_id = job_dir.name
        output_files = sorted(job_dir.glob('*.md'), key=lambda f: f.stat().st_mtime, reverse=True)
        if not output_files:
            cron_result[job_id] = {'status': 'unknown', 'reason': 'no output files'}
            continue
        recent = output_files[:7]
        ok = 0
        for f in recent:
            try:
                content = f.read_text(encoding='utf-8', errors='replace')
                if '## Response' in content:
                    resp = content.split('## Response', 1)[-1]
                    if any(kw in resp for kw in ['Traceback', 'FAILED', 'terminated']):
                        continue
                    ok += 1
                else:
                    ok += 1
            except Exception:
                pass
        total = len(recent)
        rate = round(ok/total, 2) if total > 0 else 0
        if ok == total:
            status = 'healthy'
        elif ok >= total * 0.7:
            status = 'degraded'
        else:
            status = 'failing'
        cron_result[job_id] = {'status': status, 'success_rate': rate, 'recent_runs': total}
else:
    cron_result['_error'] = 'cron output dir not found'

results['cron_health'] = cron_result

# === Skills Audit ===
skills_result = {}
if SKILLS_DIR.exists():
    total = 0
    with_doc = 0
    without_doc = []
    empty_skills = []
    outdated_skills = []
    now = datetime.now()
    for cat_dir in SKILLS_DIR.iterdir():
        if not cat_dir.is_dir():
            continue
        for skill_dir in cat_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            if skill_dir.name in ('references', 'templates', 'scripts', 'assets', '.hub') or skill_dir.name.startswith('.'):
                continue
            total += 1
            skill_md = skill_dir / 'SKILL.md'
            if skill_md.exists():
                with_doc += 1
                try:
                    content = skill_md.read_text(encoding='utf-8')
                    if len(content.strip()) < 100:
                        empty_skills.append(f'{cat_dir.name}/{skill_dir.name}')
                    mtime = datetime.fromtimestamp(skill_md.stat().st_mtime)
                    if (now - mtime).days > 30:
                        outdated_skills.append({'name': f'{cat_dir.name}/{skill_dir.name}', 'days': (now - mtime).days})
                except Exception:
                    pass
            else:
                without_doc.append(f'{cat_dir.name}/{skill_dir.name}')
    skills_result = {
        'total': total,
        'with_doc': with_doc,
        'without_doc': len(without_doc),
        'missing': without_doc[:10],
        'empty': empty_skills[:5],
        'outdated': sorted(outdated_skills, key=lambda x: -x['days'])[:10]
    }
else:
    skills_result['_error'] = 'skills dir not found'

results['skills_audit'] = skills_result

# === Git Activity (skip subprocess) ===
results['git_activity'] = {'skipped': True, 'reason': 'subprocess not available in this environment'}

# Save JSON
today = datetime.now().strftime('%Y-%m-%d')
report_file = EVOLUTION_DIR / f'analysis-{today}.json'
report_file.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

# Generate Markdown report
report_md = f"""# Agent Evolution v2 — 每日分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**系统**: Hermes Agent (自我分析)

---

## 📊 系统概览

### 🔧 Cron 任务健康

"""

if '_error' in cron_result:
    report_md += f"⚠️ {cron_result['_error']}\n\n无法获取 Cron 任务数据。\n\n"
else:
    healthy = sum(1 for v in cron_result.values() if isinstance(v, dict) and v.get('status') == 'healthy')
    degraded = sum(1 for v in cron_result.values() if isinstance(v, dict) and v.get('status') == 'degraded')
    failing = sum(1 for v in cron_result.values() if isinstance(v, dict) and v.get('status') == 'failing')
    total_jobs = len([v for v in cron_result.values() if isinstance(v, dict)])
    
    report_md += f"| 状态 | 数量 |\n|------|------|\n"
    report_md += f"| ✅ 健康 | {healthy} |\n"
    report_md += f"| ⚠️ 降级 | {degraded} |\n"
    report_md += f"| ❌ 异常 | {failing} |\n\n"
    report_md += f"**总任务数**: {total_jobs}\n\n"
    
    for job_id, job_data in cron_result.items():
        if job_id.startswith('_'):
            continue
        if job_data.get('status') in ('degraded', 'failing'):
            report_md += f"- **{job_id}** ({job_data['status']}): 成功率 {job_data.get('success_rate', 0)*100:.0f}%\n"

report_md += f"""
### 📚 技能库质量

"""

if '_error' in skills_result:
    report_md += f"⚠️ {skills_result['_error']}\n\n无法获取技能库数据。\n\n"
else:
    report_md += f"| 指标 | 数值 |\n|------|------|\n"
    report_md += f"| 总技能数 | {skills_result['total']} |\n"
    report_md += f"| 有文档 | {skills_result['with_doc']} |\n"
    report_md += f"| 缺文档 | {skills_result['without_doc']} |\n"
    report_md += f"| 内容过短 | {len(skills_result.get('empty', []))} |\n"
    report_md += f"| 超过 30 天未更新 | {len(skills_result.get('outdated', []))} |\n\n"
    
    if skills_result.get('missing'):
        report_md += "**缺少文档的技能**:\n"
        for s in skills_result['missing']:
            report_md += f"- {s}\n"
        report_md += "\n"

report_md += f"""
### 📝 项目活动

**hermes**: 数据不可用 (subprocess 不可用)
**studyai**: 数据不可用 (subprocess 不可用)
**agent_evolution**: 数据不可用 (subprocess 不可用)

---

## 🎯 改进计划

**总计**: 0 项
- 🤖 可自动执行: 0 项
- 👀 需人工审核: 0 项
- 💬 需讨论: 0 项

---

## 📋 数据获取说明

- Cron 健康分析: {'✅ 成功' if '_error' not in cron_result else '❌ 目录不存在'}
- 技能库审计: {'✅ 成功' if '_error' not in skills_result else '❌ 目录不存在'}
- Git 活动分析: ❌ 跳过 (subprocess 不可用)

---

*Agent Evolution v2 — Hermes 自我分析，数据来源于 Hermes 自身系统*
"""

md_file = EVOLUTION_DIR / f'evolution-report-{today}.md'
md_file.write_text(report_md, encoding='utf-8')

print(f"JSON: {report_file}")
print(f"MD: {md_file}")
print("DONE")
