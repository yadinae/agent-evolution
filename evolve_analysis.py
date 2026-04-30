#!/usr/bin/env python3
"""
Agent Evolution Analysis - Python Implementation
基于 agent-evolution 技能方法论的进化分析流程

整合功能:
- WAL 协议 (Write-Ahead Logging)
- Working Buffer (危险区域捕获)
- 飞书主动报告机制
- 上下文压缩恢复
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

# 配置
WORKSPACE = Path("/home/admin/.nanobot/workspace")
MEMORY_FILE = WORKSPACE / "memory" / "MEMORY.md"
HISTORY_FILE = WORKSPACE / "memory" / "HISTORY.md"
EVOLUTION_DIR = WORKSPACE / "memory" / "evolution"
REPORT_FILE = EVOLUTION_DIR / f"evolution-report-{datetime.now().strftime('%Y-%m-%d')}.md"

# 导入新增模块
sys.path.insert(0, str(Path(__file__).parent / "src"))
from wal_protocol import WALProtocol
from working_buffer import WorkingBuffer
from feishu_reporter import FeishuReporter
from task_analyzer import TaskPerformanceAnalyzer
from skill_analyzer import SkillQualityAnalyzer

# 确保输出目录存在
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)

class AgentEvolutionAnalyzer:
    """Agent 进化分析器"""
    
    def __init__(self):
        self.memory_content = ""
        self.history_content = ""
        self.improvements = []
        self.learnings = []
        self.optimizations = []
        
        # 新增：WAL 协议和工作缓冲区
        self.wal = WALProtocol()
        self.working_buffer = WorkingBuffer()
        self.reporter = FeishuReporter()
        
        # 阶段 2：增强分析能力
        self.task_analyzer = TaskPerformanceAnalyzer()
        self.skill_analyzer = SkillQualityAnalyzer()
        
        # 阶段 3：闭环进化
        self.feedback_log = EVOLUTION_DIR / "feedback-log.json"
        self.verification_results = {}
        
    def load_data(self):
        """加载历史数据"""
        print("📚 加载历史数据...")
        
        if MEMORY_FILE.exists():
            with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
                self.memory_content = f.read()
            print(f"  ✅ MEMORY.md: {len(self.memory_content)} 字节")
        else:
            print("  ⚠️ MEMORY.md 不存在")
            
        if HISTORY_FILE.exists():
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                self.history_content = f.read()
            print(f"  ✅ HISTORY.md: {len(self.history_content)} 字节")
        else:
            print("  ⚠️ HISTORY.md 不存在")
    
    def analyze_error_patterns(self):
        """分析错误模式"""
        print("\n🔍 分析错误模式...")
        
        error_patterns = [
            (r'错误|失败|Error|Failed|超时|Timeout', '错误/失败'),
            (r'401|403|404|500|502|503', 'HTTP 错误'),
            (r'API Key|凭证 | 认证 |auth', '认证问题'),
            (r'限流 |Rate Limit|quota', '速率限制'),
        ]
        
        errors = defaultdict(list)
        
        for pattern, category in error_patterns:
            matches = re.finditer(pattern, self.history_content, re.IGNORECASE)
            for match in matches:
                # 获取上下文
                start = max(0, match.start() - 100)
                end = min(len(self.history_content), match.end() + 100)
                context = self.history_content[start:end].strip()
                errors[category].append(context[:200])
        
        print(f"  发现 {sum(len(v) for v in errors.values())} 个错误事件")
        
        for category, instances in errors.items():
            if len(instances) >= 3:  # 只报告频繁错误
                self.improvements.append({
                    'type': 'error_handling',
                    'category': category,
                    'count': len(instances),
                    'suggestion': f'针对 {category} 添加自动重试和降级机制'
                })
                print(f"  ⚠️ {category}: {len(instances)} 次")
    
    def detect_consecutive_failures(self):
        """检测连续失败模式（新增）"""
        print("\n🔍 检测连续失败模式...")
        
        # 定义关键组件/阶段的失败模式（更精确，只匹配实际失败）
        critical_components = {
            'Critic 评审': [
                r'Critic 阶段.*WARNING', r'跳过评审', r'评审跳过',
                r'Critic.*超时.*跳过', r'评审超时.*跳过',
                r'Critic.*失败.*跳过', r'评审失败.*重试'
            ],
            'Hunter 搜索': [r'Hunter.*超时.*失败', r'Hunter.*失败.*重试', r'搜索超时.*跳过'],
            'Messenger 发布': [r'Messenger.*失败.*重试', r'发布失败.*重试', r'Messenger.*超时.*失败'],
            'Creator 生成': [r'Creator.*超时.*失败', r'生成失败.*重试'],
            '备份任务': [r'备份.*失败.*重试', r'backup.*failed', r'备份.*超时.*失败'],
            'Agent 进化': [r'Agent.*进化.*失败.*重试', r'evolution.*failed', r'进化任务.*失败.*重试'],
            '定时任务': [r'定时任务.*失败.*重试', r'cron.*failed', r'任务.*超时.*失败'],
        }
        
        # 提取所有带日期的行
        line_pattern = r'\[(20\d{2}-\d{2}-\d{2})[^\]]*\]\s*(.*?)(?=\n\[|$)'
        lines = re.findall(line_pattern, self.history_content, re.DOTALL)
        
        for component, patterns in critical_components.items():
            failure_dates = []
            
            for date, line in lines:
                # 检查该行是否包含任何失败模式
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        if date not in failure_dates:
                            failure_dates.append(date)
                        break
            
            # 检测连续失败
            if len(failure_dates) >= 2:
                # 检查是否连续（日期间隔<=2 天）
                failure_dates.sort(reverse=True)
                consecutive_count = 1
                max_consecutive = 1
                
                for i in range(1, len(failure_dates)):
                    try:
                        from datetime import datetime
                        d1 = datetime.strptime(failure_dates[i-1], "%Y-%m-%d")
                        d2 = datetime.strptime(failure_dates[i], "%Y-%m-%d")
                        if (d1 - d2).days <= 2:
                            consecutive_count += 1
                            max_consecutive = max(max_consecutive, consecutive_count)
                        else:
                            consecutive_count = 1
                    except:
                        pass
                
                if max_consecutive >= 2:
                    # 连续失败 2 天以上，标记为 P0 问题
                    self.improvements.append({
                        'type': 'consecutive_failure',
                        'component': component,
                        'failure_dates': failure_dates[:5],
                        'consecutive_days': max_consecutive,
                        'priority': 'P0',
                        'severity': 'critical',
                        'suggestion': f'🚨 {component} 连续 {max_consecutive} 天失败，需立即修复！'
                    })
                    print(f"  🚨 {component}: 连续 {max_consecutive} 天失败 - {failure_dates[:3]}")
    
    def analyze_workflow_efficiency(self):
        """分析工作流效率"""
        print("\n⚡ 分析工作流效率...")
        
        workflow_patterns = {
            '公众号文章': r'公众号 | 微信文章|wechat',
            '新闻简报': r'新闻简报|newsletter|AI 新闻',
            '技能开发': r'技能|skill|创建.*技能',
            '网站改进': r'studyai|网站|评审 | 改进',
            '备份任务': r'备份|backup',
            '模型切换': r'model.*switch|切换.*模型|fallback',
        }
        
        workflow_counts = {}
        
        for workflow, pattern in workflow_patterns.items():
            matches = re.findall(pattern, self.history_content, re.IGNORECASE)
            workflow_counts[workflow] = len(matches)
        
        # 找出高频任务
        for workflow, count in sorted(workflow_counts.items(), key=lambda x: -x[1]):
            if count >= 5:
                self.optimizations.append({
                    'type': 'workflow_optimization',
                    'workflow': workflow,
                    'frequency': count,
                    'suggestion': f'考虑为 {workflow} 创建专用自动化脚本或定时任务'
                })
                print(f"  📊 {workflow}: {count} 次提及")
    
    def analyze_user_corrections(self):
        """分析用户纠正"""
        print("\n📝 分析用户纠正...")
        
        correction_patterns = [
            (r'不对 | 错了|错误|not|wrong', '理解纠正'),
            (r'应该是 | 应该是|should be|correct', '正确方式'),
            (r'不要 | 禁止 | 必须 | 要求|must|require', '用户偏好'),
            (r'优先 | 首选|prefer|priority', '优先级设置'),
        ]
        
        corrections = []
        
        for pattern, category in correction_patterns:
            matches = re.finditer(pattern, self.history_content, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(self.history_content), match.end() + 150)
                context = self.history_content[start:end].strip()
                corrections.append((category, context[:250]))
        
        print(f"  发现 {len(corrections)} 个纠正/偏好记录")
        
        # 提取关键用户偏好
        user_preferences = [
            "回复末尾附带当前 Provider 和模型名称",
            "有技能就用技能，不要重复造轮子",
            "写代码前必须先头脑风暴 (OBRA 原则)",
            "子代理任务完成必须有正式回应",
            "公众号文章必须使用子代理协作流程",
            "定时任务执行时间改为东八区凌晨时段",
            "官方飞书技能比手动方式更可靠",
        ]
        
        for pref in user_preferences:
            if pref in self.history_content or pref in self.memory_content:
                self.learnings.append({
                    'type': 'user_preference',
                    'content': pref,
                    'priority': 'P0'
                })
                print(f"  ✅ 用户偏好：{pref}")
    
    def analyze_skill_usage(self):
        """分析技能使用情况"""
        print("\n🛠️ 分析技能使用情况...")
        
        # 修复：使用正确的技能路径
        skills_dir = Path("/home/admin/.hermes/skills")
        if skills_dir.exists():
            # 统计已安装技能（只计顶层技能目录）
            all_skills = []
            for cat_dir in skills_dir.iterdir():
                if cat_dir.is_dir():
                    for skill_dir in cat_dir.iterdir():
                        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                            all_skills.append(skill_dir.name)
            print(f"  已安装技能：{len(all_skills)} 个")
            
            # 检查技能文档完整性
            skills_without_docs = []
            for cat_dir in skills_dir.iterdir():
                if cat_dir.is_dir():
                    for skill_dir in cat_dir.iterdir():
                        if skill_dir.is_dir() and not (skill_dir / "SKILL.md").exists():
                            # Skip reference/template/script subdirs
                            if skill_dir.name not in ('references', 'templates', 'scripts', 'assets'):
                                skills_without_docs.append(f"{cat_dir.name}/{skill_dir.name}")
            
            if skills_without_docs:
                self.improvements.append({
                    'type': 'skill_documentation',
                    'count': len(skills_without_docs),
                    'skills': skills_without_docs[:10],
                    'suggestion': '为缺少 SKILL.md 的技能补充文档'
                })
                print(f"  ⚠️ 缺少 SKILL.md 的技能：{len(skills_without_docs)} 个")
        
        # 分析技能实际使用频率（从 HISTORY.md 中提取）
        print("\n📊 技能使用统计...")
        skill_usage = Counter()
        skill_invocation_patterns = [
            r'skill_view\(name=[\'"]([^\'"]+)[\'"]\)',
            r'skills_list',
            r'skill_manage\(action=',
        ]
        for pattern in skill_invocation_patterns:
            matches = re.findall(pattern, self.history_content)
            for m in matches:
                if isinstance(m, str) and m:
                    skill_usage[m] += 1
        
        if skill_usage:
            print(f"  检测到 {len(skill_usage)} 个技能调用记录")
            for skill, count in skill_usage.most_common(10):
                print(f"    {skill}: {count} 次")
        else:
            print("  ⚠️ 未检测到技能调用记录（HISTORY.md 中无 skill_view 调用）")
    
    def analyze_api_health(self):
        """分析 API 健康状态"""
        print("\n🏥 分析 API 健康状态...")
        
        api_issues = {
            'DashScope': self.history_content.count('401') + self.history_content.count('DashscopeException'),
            'Firecrawl': self.history_content.count('Firecrawl') + self.history_content.count('firecrawl'),
            '飞书 API': self.history_content.count('飞书') + self.history_content.count('feishu'),
            'GitHub': self.history_content.count('GitHub') + self.history_content.count('github'),
        }
        
        for api, issue_count in api_issues.items():
            if issue_count > 10:
                self.optimizations.append({
                    'type': 'api_reliability',
                    'api': api,
                    'issue_mentions': issue_count,
                    'suggestion': f'为 {api} 配置备用方案和自动降级'
                })
                print(f"  ⚠️ {api}: {issue_count} 次相关问题")
    
    def analyze_task_performance(self):
        """阶段 2：任务性能分析"""
        print("\n📊 分析任务性能...")
        
        try:
            task_analysis = self.task_analyzer.analyze_all_tasks()
            
            if 'error' in task_analysis:
                print(f"  ⚠️ {task_analysis['error']}")
                return
            
            # 提取整体健康评分
            overall = task_analysis.get('overall', {})
            print(f"  整体健康评分：{overall.get('health_score', 'N/A')}")
            print(f"  总任务数：{overall.get('total_tasks', 0)}")
            print(f"  平均成功率：{overall.get('avg_success_rate', 0)*100:.1f}%")
            
            # 提取问题任务
            tasks = task_analysis.get('tasks', {})
            problematic_tasks = []
            for task_name, task_data in tasks.items():
                health_score = task_data.get('health_score', 100)
                if health_score < 80:
                    problematic_tasks.append({
                        'name': task_name,
                        'health_score': health_score,
                        'success_rate': task_data.get('success_rate', 0),
                        'issues': task_data.get('issues', [])
                    })
            
            if problematic_tasks:
                print(f"  ⚠️ 发现 {len(problematic_tasks)} 个健康问题任务")
                for task in problematic_tasks:
                    print(f"    - {task['name']}: 健康评分 {task['health_score']}, 成功率 {task['success_rate']*100:.1f}%")
                    
                    # 添加到改进项
                    for issue in task.get('issues', []):
                        self.improvements.append({
                            'type': 'task_performance',
                            'task': task['name'],
                            'severity': issue.get('severity', 'medium'),
                            'description': issue.get('description', ''),
                            'suggestion': issue.get('suggestion', ''),
                            'health_score': task['health_score']
                        })
            
            # 提取优化建议
            recommendations = task_analysis.get('recommendations', [])
            for rec in recommendations[:5]:  # 只取前 5 个
                self.optimizations.append({
                    'type': 'task_optimization',
                    'target': rec.get('task', 'N/A'),
                    'suggestion': rec.get('suggestion', ''),
                    'priority': rec.get('priority', 'P2')
                })
            
            print(f"  ✅ 任务性能分析完成")
            
        except Exception as e:
            print(f"  ❌ 任务性能分析失败：{e}")
    
    def analyze_skill_quality(self):
        """阶段 2：技能质量分析"""
        print("\n🛠️ 分析技能质量...")
        
        try:
            skill_analysis = self.skill_analyzer.analyze_skill_library()
            
            if 'error' in skill_analysis:
                print(f"  ⚠️ {skill_analysis['error']}")
                return
            
            # 提取摘要
            summary = skill_analysis.get('summary', {})
            print(f"  评估日期：{summary.get('evaluation_date', 'N/A')}")
            print(f"  平均质量评分：{summary.get('avg_quality_score', 'N/A')}")
            
            # 提取健康分析
            health = skill_analysis.get('health_analysis', {})
            print(f"  技能总数：{health.get('total_skills', 0)}")
            print(f"  平均分数：{health.get('average_score', 0):.1f}")
            
            # 等级分布
            grade_dist = health.get('grade_distribution', {})
            print(f"  等级分布：A={grade_dist.get('A', 0)}, B={grade_dist.get('B', 0)}, C={grade_dist.get('C', 0)}, D={grade_dist.get('D', 0)}")
            
            # 提取技能缺口
            gaps = skill_analysis.get('skill_gaps', [])
            if gaps:
                print(f"  ⚠️ 发现 {len(gaps)} 个技能缺口")
                for gap in gaps:
                    print(f"    - {gap.get('title', 'N/A')}: {gap.get('description', '')}")
                    
                    # 添加到改进项
                    self.improvements.append({
                        'type': 'skill_quality',
                        'gap_type': gap.get('type', 'unknown'),
                        'severity': gap.get('severity', 'medium'),
                        'title': gap.get('title', ''),
                        'description': gap.get('description', ''),
                        'suggestion': gap.get('recommendation', ''),
                        'skills': gap.get('skills', [])
                    })
            
            # 提取优化建议
            recommendations = skill_analysis.get('recommendations', [])
            for rec in recommendations[:5]:  # 只取前 5 个
                self.optimizations.append({
                    'type': 'skill_optimization',
                    'target': rec.get('skill', 'N/A'),
                    'suggestion': rec.get('suggestion', ''),
                    'priority': rec.get('priority', 'P2')
                })
            
            print(f"  ✅ 技能质量分析完成")
            
        except Exception as e:
            print(f"  ❌ 技能质量分析失败：{e}")
    
    def _assign_priorities(self, improvements: list) -> list:
        """阶段 3：为改进项分配优先级 P0/P1/P2/P3"""
        print("\n🎯 分配改进优先级...")
        
        for imp in improvements:
            imp_type = imp.get('type', '')
            severity = imp.get('severity', 'medium')
            
            # P0：阻塞性问题（成功率<80%、安全漏洞、数据丢失）
            if imp_type in ('task_performance',) and severity == 'high':
                health_score = imp.get('health_score', 100)
                if health_score < 60:
                    imp['priority'] = 'P0'
                else:
                    imp['priority'] = 'P1'
            elif imp_type == 'error_handling' and severity == 'high':
                imp['priority'] = 'P0'
            elif imp_type == 'skill_quality' and severity == 'high':
                imp['priority'] = 'P1'
            elif imp_type in ('workflow_optimization', 'api_reliability'):
                imp['priority'] = 'P1' if severity == 'high' else 'P2'
            elif imp_type == 'skill_documentation':
                imp['priority'] = 'P2'
            else:
                imp['priority'] = 'P3'
            
            print(f"  [{imp['priority']}] {imp_type}: {imp.get('description', imp.get('title', 'N/A'))[:50]}")
        
        # 按优先级排序
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        improvements.sort(key=lambda x: priority_order.get(x.get('priority', 'P3'), 3))
        
        return improvements
    
    def _verify_improvements(self, plan: dict) -> dict:
        """阶段 3：验证上次改进效果"""
        print("\n✅ 验证改进效果...")
        
        verification = {
            'verified': [],
            'pending': [],
            'failed': [],
            'details': {}
        }
        
        # 加载历史反馈
        history = self._load_feedback_history()
        
        if not history:
            print("  ℹ️ 无历史改进记录，跳过验证")
            return verification
        
        # 检查上次周期的改进项
        last_cycle = history.get('last_cycle', 0)
        current_cycle = plan.get('cycle', 0)
        
        if last_cycle >= current_cycle:
            print(f"  ℹ️ 周期 {last_cycle} 已验证，跳过")
            return verification
        
        last_improvements = history.get('last_improvements', [])
        
        for imp in last_improvements:
            imp_id = imp.get('id', '')
            imp_type = imp.get('type', '')
            applied = imp.get('applied', False)
            
            if not applied:
                verification['pending'].append(imp_id)
                continue
            
            # 验证逻辑：根据改进类型检查是否生效
            status = self._verify_single_improvement(imp)
            
            if status == 'effective':
                verification['verified'].append(imp_id)
                verification['details'][imp_id] = {
                    'status': 'effective',
                    'message': '改进已生效'
                }
            elif status == 'partial':
                verification['pending'].append(imp_id)
                verification['details'][imp_id] = {
                    'status': 'partial',
                    'message': '改进部分生效，需持续关注'
                }
            else:
                verification['failed'].append(imp_id)
                verification['details'][imp_id] = {
                    'status': 'failed',
                    'message': '改进未生效，需重新评估'
                }
        
        print(f"  验证结果：✅ {len(verification['verified'])} 个有效, "
              f"⏳ {len(verification['pending'])} 个待观察, "
              f"❌ {len(verification['failed'])} 个失败")
        
        self.verification_results = verification
        return verification
    
    def _verify_single_improvement(self, imp: dict) -> str:
        """验证单个改进是否生效"""
        imp_type = imp.get('type', '')
        
        if imp_type == 'skill_documentation':
            # 验证技能文档是否已创建
            skills = imp.get('skills', [])
            for skill_path in skills:
                if '/' in skill_path:
                    cat, name = skill_path.split('/', 1)
                    skill_md = Path(f"/home/admin/.hermes/skills/{cat}/{name}/SKILL.md")
                    if skill_md.exists():
                        return 'effective'
            return 'failed'
        
        elif imp_type == 'error_handling':
            # 验证错误频次是否下降
            category = imp.get('category', '')
            current_count = self.history_content.count(category) if category else 0
            last_count = imp.get('last_count', 0)
            if last_count > 0 and current_count < last_count * 0.8:
                return 'effective'
            elif last_count > 0 and current_count < last_count:
                return 'partial'
            return 'pending'
        
        elif imp_type == 'task_performance':
            # 验证任务健康评分是否提升
            task_name = imp.get('task', '')
            last_score = imp.get('last_health_score', 0)
            # 简化：如果任务名出现在当前改进中，说明问题仍在
            current_issues = [i for i in self.improvements if i.get('task') == task_name]
            if not current_issues:
                return 'effective'
            elif last_score > 0:
                return 'partial'
            return 'pending'
        
        elif imp_type == 'skill_quality':
            # 验证技能缺口是否已填补
            skills = imp.get('skills', [])
            if skills:
                # 检查技能是否已创建或改进
                return 'pending'  # 需要人工验证
            return 'pending'
        
        return 'pending'
    
    def _record_feedback(self, plan: dict, applied: list, verification: dict):
        """阶段 3：记录反馈循环"""
        print("\n📝 记录反馈循环...")
        
        # 加载现有反馈
        feedback = self._load_feedback_history()
        if not feedback:
            feedback = {
                'cycles': [],
                'last_cycle': 0,
                'last_improvements': []
            }
        
        # 记录当前周期
        cycle_record = {
            'cycle': plan.get('cycle', 0),
            'timestamp': datetime.now().isoformat(),
            'improvements_count': len(plan.get('improvements', [])),
            'applied_count': len(applied),
            'verification': {
                'verified': len(verification.get('verified', [])),
                'pending': len(verification.get('pending', [])),
                'failed': len(verification.get('failed', []))
            },
            'applied_improvements': applied,
            'verification_details': verification.get('details', {})
        }
        
        feedback['cycles'].append(cycle_record)
        feedback['last_cycle'] = plan.get('cycle', 0)
        feedback['last_improvements'] = [
            {
                'id': f"{imp.get('type', '')}-{imp.get('task', imp.get('category', imp.get('title', '')))}",
                'type': imp.get('type', ''),
                'applied': imp.get('type', '') in [a.get('type', '') for a in applied],
                'priority': imp.get('priority', 'P3')
            }
            for imp in plan.get('improvements', [])
        ]
        
        # 只保留最近 10 个周期
        if len(feedback['cycles']) > 10:
            feedback['cycles'] = feedback['cycles'][-10:]
        
        # 保存反馈
        with open(self.feedback_log, 'w', encoding='utf-8') as f:
            json.dump(feedback, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 反馈已保存：{self.feedback_log}")
        print(f"  周期 {cycle_record['cycle']}: "
              f"应用 {len(applied)}/{len(plan.get('improvements', []))} 个改进, "
              f"验证 {len(verification.get('verified', []))} 个有效")
    
    def _load_feedback_history(self) -> dict:
        """加载历史反馈记录"""
        if self.feedback_log.exists():
            try:
                with open(self.feedback_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"  ⚠️ 加载反馈历史失败：{e}")
        return None
    
    def generate_evolution_plan(self):
        """生成进化计划"""
        print("\n📋 生成进化计划...")
        
        plan = {
            'timestamp': datetime.now().isoformat(),
            'cycle': self._get_evolution_cycle(),
            'improvements': self.improvements,
            'learnings': self.learnings,
            'optimizations': self.optimizations,
        }
        
        # 保存进化计划
        plan_file = EVOLUTION_DIR / f"evolution-plan-{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(plan_file, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 进化计划已保存：{plan_file}")
        return plan
    
    def _get_evolution_cycle(self) -> int:
        """获取进化周期数（并写回状态）"""
        state_file = EVOLUTION_DIR / "evolution_state.json"
        cycle = 1
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                cycle = state.get('cycle', 0) + 1
        else:
            state = {}
        
        # 写回状态（修复 cycle 始终为 1 的 bug）
        state['cycle'] = cycle
        state['last_run'] = datetime.now().isoformat()
        with open(state_file, 'w') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        return cycle
    
    def generate_report(self, plan, trend=None, verification=None):
        """生成进化报告"""
        print("\n📄 生成进化报告...")
        
        report = f"""# Agent Evolution Report - 进化报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**进化周期**: #{plan['cycle']}  
**数据源**: MEMORY.md + HISTORY.md

---

## 📊 分析摘要

### 改进机会 (Improvements)
共发现 **{len(self.improvements)}** 个改进机会

"""
        
        for i, imp in enumerate(self.improvements, 1):
            report += f"""
#### {i}. {imp['type'].replace('_', ' ').title()}
- **建议**: {imp.get('suggestion', 'N/A')}
"""
            if 'count' in imp:
                report += f"- **频次**: {imp['count']}\n"
            if 'category' in imp:
                report += f"- **类别**: {imp['category']}\n"
        
        report += f"""
### 学习记录 (Learnings)
共记录 **{len(self.learnings)}** 条用户偏好

"""
        
        for i, learn in enumerate(self.learnings, 1):
            report += f"""
#### {i}. {learn['content']}
- **优先级**: {learn.get('priority', 'P1')}
- **类型**: {learn['type']}
"""
        
        report += f"""
### 优化建议 (Optimizations)
共提出 **{len(self.optimizations)}** 个优化建议

"""
        
        for i, opt in enumerate(self.optimizations, 1):
            report += f"""
#### {i}. {opt['type'].replace('_', ' ').title()}
- **目标**: {opt.get('workflow', opt.get('api', 'N/A'))}
- **建议**: {opt.get('suggestion', 'N/A')}
"""
            if 'frequency' in opt:
                report += f"- **频次**: {opt['frequency']}\n"
        
        # 阶段 2：任务性能分析结果
        report += f"""
### 📊 任务性能分析

"""
        # 从 improvements 中提取任务性能相关项
        task_improvements = [i for i in self.improvements if i.get('type') == 'task_performance']
        task_optimizations = [o for o in self.optimizations if o.get('type') == 'task_optimization']
        
        if task_improvements:
            report += f"**问题任务**: {len(task_improvements)} 个\n\n"
            for imp in task_improvements[:5]:
                report += f"- **{imp.get('task', 'N/A')}**: {imp.get('description', '')}\n"
                report += f"  - 建议：{imp.get('suggestion', '')}\n"
        else:
            report += "✅ 所有任务运行正常\n"
        
        if task_optimizations:
            report += f"\n**优化建议**: {len(task_optimizations)} 个\n\n"
            for opt in task_optimizations[:3]:
                report += f"- **{opt.get('target', 'N/A')}**: {opt.get('suggestion', '')}\n"
        
        # 阶段 2：技能质量分析结果
        report += f"""
### 🛠️ 技能质量分析

"""
        # 从 improvements 中提取技能质量相关项
        skill_improvements = [i for i in self.improvements if i.get('type') == 'skill_quality']
        skill_optimizations = [o for o in self.optimizations if o.get('type') == 'skill_optimization']
        
        if skill_improvements:
            report += f"**技能缺口**: {len(skill_improvements)} 个\n\n"
            for imp in skill_improvements[:5]:
                report += f"- **{imp.get('title', 'N/A')}**: {imp.get('description', '')}\n"
                report += f"  - 建议：{imp.get('suggestion', '')}\n"
        else:
            report += "✅ 技能库健康状况良好\n"
        
        if skill_optimizations:
            report += f"\n**优化建议**: {len(skill_optimizations)} 个\n\n"
            for opt in skill_optimizations[:3]:
                report += f"- **{opt.get('target', 'N/A')}**: {opt.get('suggestion', '')}\n"
        
        report += f"""
---

"""
        # 添加趋势对比（如果有）
        if trend:
            report += f"""## 📈 趋势对比（vs 上一周期）

| 指标 | 上一周期 | 本周期 | 变化 |
|------|---------|--------|------|
| 改进机会 | {trend['improvements']['yesterday']} | {trend['improvements']['today']} | {trend['improvements']['direction']} ({trend['improvements']['change']:+d}) |
| 优化建议 | {trend['optimizations']['yesterday']} | {trend['optimizations']['today']} | {trend['optimizations']['direction']} ({trend['optimizations']['change']:+d}) |
| 学习记录 | {trend['learnings']['yesterday']} | {trend['learnings']['today']} | {trend['learnings']['direction']} ({trend['learnings']['change']:+d}) |
"""
            if trend.get('new_issues'):
                report += f"\n### 🆕 新增问题\n"
                for issue in trend['new_issues']:
                    report += f"- {issue}\n"
            
            if trend.get('resolved_issues'):
                report += f"\n### ✅ 已解决问题\n"
                for issue in trend['resolved_issues']:
                    report += f"- {issue}\n"
            
            if trend.get('persistent_issues'):
                report += f"\n### ⏳ 持续问题（多周期未解决）\n"
                for issue in trend['persistent_issues']:
                    report += f"- {issue}\n"
            
            report += "\n---\n\n"
        
        report += f"""## 🎯 执行建议

### 立即执行 (P0)
1. 将用户偏好记录到 MEMORY.md 和 AGENTS.md
2. 为高频工作流创建自动化脚本
3. 修复缺少文档的技能

### 短期执行 (P1)
1. 为关键 API 配置备用方案
2. 优化错误处理和重试机制
3. 完善技能文档

### 长期执行 (P2)
1. 建立技能使用统计系统
2. 实现自动进化循环

---

"""
        # 阶段 3：改进效果验证
        if verification:
            report += f"""## ✅ 改进效果验证

| 状态 | 数量 |
|------|------|
| ✅ 已验证有效 | {len(verification.get('verified', []))} |
| ⏳ 待观察 | {len(verification.get('pending', []))} |
| ❌ 未生效 | {len(verification.get('failed', []))} |

"""
            if verification.get('details'):
                report += "### 验证详情\n\n"
                for imp_id, detail in verification['details'].items():
                    status_emoji = {'effective': '✅', 'partial': '⏳', 'failed': '❌'}.get(detail['status'], '❓')
                    report += f"- {status_emoji} **{imp_id}**: {detail['message']}\n"
                report += "\n"
        
        # 阶段 3：反馈循环摘要
        feedback = self._load_feedback_history()
        if feedback and feedback.get('cycles'):
            report += f"""## 📝 反馈循环摘要

**记录周期数**: {len(feedback['cycles'])}

| 周期 | 改进数 | 应用数 | 验证有效 | 待观察 | 失败 |
|------|--------|--------|----------|--------|------|
"""
            for cycle in feedback['cycles'][-5:]:  # 最近 5 个周期
                v = cycle.get('verification', {})
                report += f"| #{cycle['cycle']} | {cycle['improvements_count']} | {cycle['applied_count']} | {v.get('verified', 0)} | {v.get('pending', 0)} | {v.get('failed', 0)} |\n"
            report += "\n"
        
        report += f"""---

## 📁 输出文件

- 进化计划：`memory/evolution/evolution-plan-{datetime.now().strftime('%Y-%m-%d')}.json`
- 本报告：`memory/evolution/evolution-report-{datetime.now().strftime('%Y-%m-%d')}.md`

---

*Generated by Agent Evolution Analyzer v1.0*
"""
        
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"  ✅ 进化报告已保存：{REPORT_FILE}")
        return report
    
    def run(self):
        """执行完整进化流程"""
        print("=" * 60)
        print("🧬 Agent Evolution - Agent 自我进化流程")
        print("=" * 60)
        
        # 0. WAL 协议：记录开始状态
        self.wal.log_entry("evolution_start", {
            "trigger": "heartbeat",
            "timestamp": datetime.now().isoformat(),
            "source_files": ["MEMORY.md", "HISTORY.md"]
        }, before_action=True)
        
        # 0. 更新会话状态
        self.wal.update_session_state({
            "current_task": "agent_evolution",
            "phase": "initializing",
            "started_at": datetime.now().isoformat()
        })
        
        # 1. 加载数据
        self.load_data()
        
        # 2. 分析错误模式
        self.analyze_error_patterns()
        
        # 2.5. 检测连续失败模式（新增）
        self.detect_consecutive_failures()
        
        # 3. 分析工作流效率
        self.analyze_workflow_efficiency()
        
        # 4. 分析用户纠正
        self.analyze_user_corrections()
        
        # 5. 分析技能使用情况
        self.analyze_skill_usage()
        
        # 6. 分析 API 健康状态
        self.analyze_api_health()
        
        # 6.5. 阶段 2：任务性能分析
        self.analyze_task_performance()
        
        # 6.6. 阶段 2：技能质量分析
        self.analyze_skill_quality()
        
        # 7. 生成进化计划
        plan = self.generate_evolution_plan()
        
        # 7.5. 趋势对比分析（与上一周期对比）
        trend = self._compare_with_last_cycle(plan)
        
        # 7.6. 自动应用安全改进
        applied = self._apply_safe_improvements(plan)
        
        # 阶段 3：优先级排序
        plan['improvements'] = self._assign_priorities(plan.get('improvements', []))
        
        # 阶段 3：验证改进效果
        verification = self._verify_improvements(plan)
        
        # 阶段 3：记录反馈循环
        self._record_feedback(plan, applied, verification)
        
        # 8. 生成进化报告
        report = self.generate_report(plan, trend, verification)
        
        # 9. 更新会话状态：完成
        self.wal.update_session_state({
            "current_task": "agent_evolution",
            "phase": "completed",
            "completed_at": datetime.now().isoformat(),
            "report_path": str(REPORT_FILE)
        })
        
        # 10. 飞书主动报告（仅在**新增**异常或重要事件时发送）
        try:
            print("\n📤 检查是否需要发送飞书报告...")
            # 查找上次报告（用于对比检测新增异常）
            last_report = self._find_last_report()
            
            # 检查报告中是否有**新增**异常或重要事件
            has_anomaly = self.reporter.check_report_for_anomalies(str(REPORT_FILE), last_report)
            
            if has_anomaly:
                print("  ⚠️  检测到新增异常 - 发送飞书通知")
                result = self.reporter.send_evolution_report(str(REPORT_FILE), force_send=True)
                print("✅ 飞书报告已发送")
            else:
                print("  ✅ 无新增异常 - 静默模式跳过通知")
                result = {"status": "skipped", "reason": "no_new_anomaly"}
        except Exception as e:
            print(f"⚠️ 飞书报告发送失败：{e}")
            result = None
            has_anomaly = False
        
        # 11. 清理 HEARTBEAT.md 历史记录（只保留最近 3 条）
        try:
            print("\n🧹 清理历史记录...")
            self._cleanup_heartbeat_history()
            print("✅ 历史记录已清理（保留最近 3 条）")
        except Exception as e:
            print(f"⚠️ 历史记录清理失败：{e}")
        
        print("\n" + "=" * 60)
        print("✅ 进化流程完成!")
        print("=" * 60)
        date_str = datetime.now().strftime('%Y-%m-%d')
        print(f"\n📁 输出文件:")
        print(f"   - {REPORT_FILE}")
        print(f"   - {EVOLUTION_DIR / f'evolution-plan-{date_str}.json'}")
        print(f"   - {WORKSPACE / 'memory' / 'wal-protocol.md'}")
        print(f"   - {WORKSPACE / 'SESSION-STATE.md'}")
        print(f"   - {WORKSPACE / 'memory' / 'working-buffer.md'}")
        
        return {
            'improvements': len(self.improvements),
            'learnings': len(self.learnings),
            'optimizations': len(self.optimizations),
            'report_path': str(REPORT_FILE),
            'has_anomaly': has_anomaly,
            'notification_sent': has_anomaly,
            'trend': trend if trend else {},
            'applied_improvements': applied if applied else []
        }
    
    def _check_for_anomalies(self) -> bool:
        """
        检查是否有异常或重要事件需要发送通知
        
        Returns:
            bool: True 表示有异常需要发送通知，False 表示无异常可以静默
        """
        # 检查错误数量是否超过阈值
        error_threshold = 1000  # 错误数超过 1000 视为异常
        
        # 检查是否有严重错误模式
        critical_patterns = [
            r'严重错误|Critical|Fatal',
            r'系统崩溃|System Crash',
            r'数据丢失|Data Loss',
            r'API 配额耗尽|Quota Exhausted',
        ]
        
        # 检查是否有 P0 级别的用户纠正
        p0_pattern = r'P0|优先级.*0|最高优先级'
        
        # 检查错误数量
        error_count = sum(len(v) for v in self.errors.values()) if hasattr(self, 'errors') else 0
        
        # 检查是否有严重错误
        has_critical_error = any(
            re.search(pattern, self.history_content, re.IGNORECASE)
            for pattern in critical_patterns
        )
        
        # 检查是否有 P0 纠正
        has_p0_correction = bool(re.search(p0_pattern, self.history_content, re.IGNORECASE))
        
        # 检查改进项中是否有 P0 优先级
        has_p0_improvement = any(
            imp.get('priority') == 'P0' or imp.get('severity') == 'critical'
            for imp in self.improvements
        )
        
        # 综合判断
        has_anomaly = (
            error_count > error_threshold or
            has_critical_error or
            has_p0_correction or
            has_p0_improvement
        )
        
        if has_anomaly:
            print(f"  检测到异常：错误数={error_count}, 严重错误={has_critical_error}, P0 纠正={has_p0_correction}, P0 改进={has_p0_improvement}")
        
        return has_anomaly
    
    def _compare_with_last_cycle(self, current_plan: dict) -> dict:
        """与上一周期对比，生成趋势报告"""
        print("\n📈 趋势对比分析...")
        
        # 查找昨天的进化计划
        import glob
        plan_pattern = str(EVOLUTION_DIR / "evolution-plan-*.json")
        plans = sorted(glob.glob(plan_pattern))
        
        if len(plans) < 2:
            print("  ⚠️ 没有足够的历史数据进行趋势对比")
            return {}
        
        # 加载昨天的计划
        yesterday_plan_path = plans[-2]  # 倒数第二个（最新的是今天的）
        try:
            with open(yesterday_plan_path, 'r') as f:
                yesterday_plan = json.load(f)
        except (json.JSONDecodeError, IOError):
            print("  ⚠️ 无法加载昨天的进化计划")
            return {}
        
        # 提取关键指标
        today_improvements = len(current_plan.get('improvements', []))
        yesterday_improvements = len(yesterday_plan.get('improvements', []))
        today_optimizations = len(current_plan.get('optimizations', []))
        yesterday_optimizations = len(yesterday_plan.get('optimizations', []))
        today_learnings = len(current_plan.get('learnings', []))
        yesterday_learnings = len(yesterday_plan.get('learnings', []))
        
        # 计算趋势
        trend = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'cycle': current_plan.get('cycle', 1),
            'improvements': {
                'today': today_improvements,
                'yesterday': yesterday_improvements,
                'change': today_improvements - yesterday_improvements,
                'direction': '↑' if today_improvements > yesterday_improvements else ('↓' if today_improvements < yesterday_improvements else '→')
            },
            'optimizations': {
                'today': today_optimizations,
                'yesterday': yesterday_optimizations,
                'change': today_optimizations - yesterday_optimizations,
                'direction': '↑' if today_optimizations > yesterday_optimizations else ('↓' if today_optimizations < yesterday_optimizations else '→')
            },
            'learnings': {
                'today': today_learnings,
                'yesterday': yesterday_learnings,
                'change': today_learnings - yesterday_learnings,
                'direction': '↑' if today_learnings > yesterday_learnings else ('↓' if today_learnings < yesterday_learnings else '→')
            }
        }
        
        # 对比具体的改进项，识别新增和已解决的
        today_imp_types = set(i.get('type', '') + ':' + i.get('category', i.get('workflow', '')) for i in current_plan.get('improvements', []))
        yesterday_imp_types = set(i.get('type', '') + ':' + i.get('category', i.get('workflow', '')) for i in yesterday_plan.get('improvements', []))
        
        trend['new_issues'] = list(today_imp_types - yesterday_imp_types)
        trend['resolved_issues'] = list(yesterday_imp_types - today_imp_types)
        trend['persistent_issues'] = list(today_imp_types & yesterday_imp_types)
        
        # 打印趋势
        print(f"  改进机会: {yesterday_improvements} → {today_improvements} {trend['improvements']['direction']} (变化: {trend['improvements']['change']:+d})")
        print(f"  优化建议: {yesterday_optimizations} → {today_optimizations} {trend['optimizations']['direction']} (变化: {trend['optimizations']['change']:+d})")
        print(f"  学习记录: {yesterday_learnings} → {today_learnings} {trend['learnings']['direction']} (变化: {trend['learnings']['change']:+d})")
        
        if trend['new_issues']:
            print(f"  🆕 新增问题: {len(trend['new_issues'])} 个")
            for issue in trend['new_issues']:
                print(f"    + {issue}")
        
        if trend['resolved_issues']:
            print(f"  ✅ 已解决问题: {len(trend['resolved_issues'])} 个")
            for issue in trend['resolved_issues']:
                print(f"    - {issue}")
        
        if trend['persistent_issues']:
            print(f"  ⏳ 持续问题: {len(trend['persistent_issues'])} 个")
            for issue in trend['persistent_issues']:
                print(f"    * {issue}")
        
        return trend
    
    def _apply_safe_improvements(self, plan: dict):
        """自动应用安全的改进项"""
        print("\n🔧 自动应用安全改进...")
        
        applied = []
        
        for imp in plan.get('improvements', []):
            imp_type = imp.get('type', '')
            
            # 技能文档补充是安全的自动改进
            if imp_type == 'skill_documentation':
                skills = imp.get('skills', [])
                for skill_path in skills:
                    # 跳过已知是插件 stub 的技能
                    if '/' in skill_path:
                        cat, name = skill_path.split('/', 1)
                        skill_dir = Path(f"/home/admin/.hermes/skills/{cat}/{name}")
                    else:
                        continue
                    
                    if not skill_dir.exists():
                        continue
                    
                    skill_md = skill_dir / "SKILL.md"
                    if not skill_md.exists():
                        # 检查是否有 DESCRIPTION.md（插件 stub）
                        desc_md = skill_dir / "DESCRIPTION.md"
                        if desc_md.exists():
                            try:
                                desc_content = desc_md.read_text(encoding='utf-8')
                                # 提取 description
                                import re
                                desc_match = re.search(r'description:\s*[\'"]?(.+?)[\'"]?\s*$', desc_content, re.MULTILINE)
                                if desc_match:
                                    description = desc_match.group(1).strip()
                                    # 创建基础 SKILL.md
                                    skill_content = f"""---
name: {name}
description: {description}
category: {cat}
---

# {name.replace('-', ' ').title()}

{description}

## Overview

This skill is auto-generated from plugin metadata. Full documentation pending.

## Usage

See plugin documentation for usage details.
"""
                                    skill_md.write_text(skill_content, encoding='utf-8')
                                    applied.append(f"为 {skill_path} 创建基础 SKILL.md")
                                    print(f"  ✅ 已为 {skill_path} 创建基础 SKILL.md")
                            except Exception as e:
                                print(f"  ⚠️ 创建 {skill_path} SKILL.md 失败: {e}")
        
        if not applied:
            print("  ℹ️  无安全改进可自动应用")
        
        return applied
    
    def _find_last_report(self) -> str:
        """
        查找上次的进化报告文件路径
        
        Returns:
            str: 上次报告的文件路径，如果不存在则返回 None
        """
        import glob
        
        # 获取所有报告文件
        report_pattern = str(EVOLUTION_DIR / "evolution-report-*.md")
        reports = glob.glob(report_pattern)
        
        if not reports:
            return None
        
        # 按文件名排序（日期排序）
        reports.sort(reverse=True)
        
        # 返回第二新的报告（最新的是当前报告）
        if len(reports) >= 2:
            return reports[1]
        
        return None
    
    def _cleanup_heartbeat_history(self, keep_count: int = 3):
        """
        清理 HEARTBEAT.md 中的历史执行记录，只保留最近 N 条
        
        Args:
            keep_count: 保留的记录数量（默认 3 条）
        """
        heartbeat_file = WORKSPACE / "memory" / "HEARTBEAT.md"
        if not heartbeat_file.exists():
            return
        
        with open(heartbeat_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割文件内容
        parts = content.split('### 🧬 Agent 进化任务')
        if len(parts) < 2:
            return
        
        header = parts[0]
        footer_parts = parts[1].split('### 🧠 MemTensor-X 任务')
        
        if len(footer_parts) < 2:
            return
        
        evolution_section = footer_parts[0]
        memtensor_section = footer_parts[1]
        
        # 提取所有执行记录
        import re
        records = re.findall(r'- \[x\] \*\*.*?(?=- \[x\] \*\*|### 🧠|$)', evolution_section, re.DOTALL)
        
        # 只保留最近 N 条
        if len(records) > keep_count:
            recent_records = records[:keep_count]
            
            # 重建文件内容
            new_content = header
            new_content += '### 🧬 Agent 进化任务\n\n'
            new_content += ''.join(recent_records)
            new_content += '\n### 🧠 MemTensor-X 任务'
            new_content += memtensor_section
            
            # 写入文件
            with open(heartbeat_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  已清理 {len(records) - keep_count} 条历史记录，保留 {keep_count} 条")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Agent Evolution Analysis')
    parser.add_argument('--analyze', action='store_true', help='分析会话历史（运行完整进化流程）')
    parser.add_argument('--daily-review', action='store_true', help='每日审查（运行完整进化流程）')
    parser.add_argument('--weekly-summary', action='store_true', help='每周总结（运行完整进化流程）')
    
    args = parser.parse_args()
    
    analyzer = AgentEvolutionAnalyzer()
    
    # 所有模式都运行完整进化流程
    result = analyzer.run()
    
    # 输出 JSON 结果供后续处理
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
