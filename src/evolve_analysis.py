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
        
        skills_dir = WORKSPACE / "skills"
        if skills_dir.exists():
            skill_count = len([d for d in skills_dir.iterdir() if d.is_dir()])
            print(f"  已安装技能：{skill_count} 个")
            
            # 检查技能文档完整性
            skills_without_docs = []
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_md = skill_dir / "SKILL.md"
                    if not skill_md.exists():
                        skills_without_docs.append(skill_dir.name)
            
            if skills_without_docs:
                self.improvements.append({
                    'type': 'skill_documentation',
                    'count': len(skills_without_docs),
                    'skills': skills_without_docs[:10],
                    'suggestion': '为缺少 SKILL.md 的技能补充文档'
                })
                print(f"  ⚠️ 缺少 SKILL.md 的技能：{len(skills_without_docs)} 个")
    
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
    
    def _get_evolution_cycle(self):
        """获取进化周期数"""
        state_file = EVOLUTION_DIR / "evolution_state.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                state = json.load(f)
                return state.get('cycle', 0) + 1
        return 1
    
    def generate_report(self, plan):
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
        
        report += f"""
---

## 🎯 执行建议

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
3. 集成 OpenSpace MCP 进行技能进化

---

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
        
        # 3. 分析工作流效率
        self.analyze_workflow_efficiency()
        
        # 4. 分析用户纠正
        self.analyze_user_corrections()
        
        # 5. 分析技能使用情况
        self.analyze_skill_usage()
        
        # 6. 分析 API 健康状态
        self.analyze_api_health()
        
        # 7. 生成进化计划
        plan = self.generate_evolution_plan()
        
        # 8. 生成进化报告
        report = self.generate_report(plan)
        
        # 9. 更新会话状态：完成
        self.wal.update_session_state({
            "current_task": "agent_evolution",
            "phase": "completed",
            "completed_at": datetime.now().isoformat(),
            "report_path": str(REPORT_FILE)
        })
        
        # 10. 飞书主动报告（仅在异常或重要事件时发送）
        try:
            print("\n📤 检查是否需要发送飞书报告...")
            # 检查报告中是否有异常或重要事件
            has_anomaly = self.reporter.check_report_for_anomalies(str(REPORT_FILE))
            
            if has_anomaly:
                print("  ⚠️  检测到异常 - 发送飞书通知")
                result = self.reporter.send_evolution_report(str(REPORT_FILE), force_send=True)
                print("✅ 飞书报告已发送")
            else:
                print("  ✅ 无异常 - 静默模式跳过通知")
                result = self.reporter.send_evolution_report(str(REPORT_FILE), force_send=False)
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
            'notification_sent': has_anomaly
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
    analyzer = AgentEvolutionAnalyzer()
    result = analyzer.run()
    
    # 输出 JSON 结果供后续处理
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
