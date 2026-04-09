#!/usr/bin/env python3
"""
任务性能分析器

功能:
- 读取任务监控数据
- 分析任务执行模式
- 识别优化机会
- 生成优化建议

用法:
    from task_analyzer import TaskPerformanceAnalyzer
    
    analyzer = TaskPerformanceAnalyzer()
    analysis = analyzer.analyze_all_tasks()
    print(analysis)
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import json


class TaskPerformanceAnalyzer:
    """任务性能分析器"""
    
    def __init__(self,
                 task_monitoring_db: str = "/home/admin/.nanobot/workspace/task-monitoring.db",
                 quality_db: str = "/home/admin/.nanobot/workspace/skill-quality.db"):
        self.task_monitoring_db = Path(task_monitoring_db)
        self.quality_db = Path(quality_db)
    
    def analyze_all_tasks(self) -> Dict[str, Any]:
        """分析所有任务的性能"""
        if not self.task_monitoring_db.exists():
            return {'error': 'Task monitoring database not found'}
        
        # 获取所有任务
        tasks = self._get_all_tasks()
        
        # 分析每个任务
        task_analyses = {}
        for task in tasks:
            task_analyses[task['task_name']] = self._analyze_single_task(task['task_name'])
        
        # 生成整体分析
        overall_analysis = self._generate_overall_analysis(task_analyses)
        
        # 生成优化建议
        recommendations = self._generate_recommendations(task_analyses, overall_analysis)
        
        return {
            'analysis_date': datetime.now().isoformat(),
            'overall': overall_analysis,
            'tasks': task_analyses,
            'recommendations': recommendations
        }
    
    def _get_all_tasks(self) -> List[Dict[str, Any]]:
        """获取所有任务列表"""
        conn = sqlite3.connect(self.task_monitoring_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT task_name, task_type
            FROM task_executions
            ORDER BY task_name
        """)
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return tasks
    
    def _analyze_single_task(self, task_name: str) -> Dict[str, Any]:
        """分析单个任务的性能"""
        conn = sqlite3.connect(self.task_monitoring_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取最近 30 天的执行记录
        cursor.execute("""
            SELECT 
                COUNT(*) as total_executions,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                AVG(duration_seconds) as avg_duration,
                MIN(duration_seconds) as min_duration,
                MAX(duration_seconds) as max_duration,
                AVG(input_tokens + output_tokens) as avg_tokens,
                SUM(input_tokens + output_tokens) as total_tokens
            FROM task_executions
            WHERE task_name = ?
            AND scheduled_time >= datetime('now', '-30 days')
        """, (task_name,))
        
        stats = dict(cursor.fetchone())
        
        # 获取错误分布
        cursor.execute("""
            SELECT error_type, COUNT(*) as count
            FROM task_executions
            WHERE task_name = ?
            AND status != 'success'
            AND scheduled_time >= datetime('now', '-30 days')
            GROUP BY error_type
            ORDER BY count DESC
            LIMIT 5
        """, (task_name,))
        
        error_distribution = [dict(row) for row in cursor.fetchall()]
        
        # 获取执行趋势（按天聚合）
        cursor.execute("""
            SELECT 
                DATE(scheduled_time) as date,
                COUNT(*) as executions,
                AVG(duration_seconds) as avg_duration,
                SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate
            FROM task_executions
            WHERE task_name = ?
            AND scheduled_time >= datetime('now', '-30 days')
            GROUP BY DATE(scheduled_time)
            ORDER BY date DESC
            LIMIT 30
        """, (task_name,))
        
        trend_data = [dict(row) for row in cursor.fetchall()]
        
        # 获取阶段性能（如果有）
        cursor.execute("""
            SELECT stage_name, AVG(duration_seconds) as avg_duration,
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate
            FROM execution_stages
            WHERE task_name = ?
            AND created_at >= datetime('now', '-30 days')
            GROUP BY stage_name
        """, (task_name,))
        
        stage_performance = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        # 计算成功率
        success_rate = stats['success_count'] / stats['total_executions'] if stats['total_executions'] > 0 else 0
        
        # 识别问题
        issues = self._identify_task_issues(stats, success_rate, error_distribution)
        
        return {
            'task_name': task_name,
            'statistics': stats,
            'success_rate': success_rate,
            'error_distribution': error_distribution,
            'trend_data': trend_data,
            'stage_performance': stage_performance,
            'issues': issues,
            'health_score': self._calculate_health_score(stats, success_rate, error_distribution)
        }
    
    def _identify_task_issues(self, stats: Dict, success_rate: float, 
                              error_distribution: List[Dict]) -> List[Dict[str, str]]:
        """识别任务问题"""
        issues = []
        
        # 成功率低
        if success_rate < 0.8:
            issues.append({
                'type': 'low_success_rate',
                'severity': 'high',
                'description': f'成功率仅 {success_rate*100:.1f}%，低于 80% 阈值',
                'suggestion': '检查错误日志，优化错误处理和重试机制'
            })
        elif success_rate < 0.95:
            issues.append({
                'type': 'moderate_success_rate',
                'severity': 'medium',
                'description': f'成功率 {success_rate*100:.1f}%，低于 95% 目标',
                'suggestion': '分析失败原因，改进稳定性'
            })
        
        # 执行时间长
        if stats['avg_duration'] and stats['avg_duration'] > 300:  # 5 分钟
            issues.append({
                'type': 'long_duration',
                'severity': 'high',
                'description': f'平均执行时间 {stats["avg_duration"]:.1f}秒，超过 5 分钟',
                'suggestion': '优化任务逻辑，考虑拆分任务或增加并行处理'
            })
        elif stats['avg_duration'] and stats['avg_duration'] > 120:  # 2 分钟
            issues.append({
                'type': 'moderate_duration',
                'severity': 'medium',
                'description': f'平均执行时间 {stats["avg_duration"]:.1f}秒，较长',
                'suggestion': '分析耗时阶段，优化性能瓶颈'
            })
        
        # Token 消耗大
        if stats['avg_tokens'] and stats['avg_tokens'] > 50000:
            issues.append({
                'type': 'high_token_usage',
                'severity': 'medium',
                'description': f'平均消耗 {stats["avg_tokens"]:.0f} tokens，较高',
                'suggestion': '优化提示词，减少不必要的上下文'
            })
        
        # 特定错误类型
        for error in error_distribution:
            if error['count'] >= 3:
                issues.append({
                    'type': 'frequent_error',
                    'severity': 'high' if error['count'] >= 5 else 'medium',
                    'description': f'频繁出现错误：{error["error_type"]} ({error["count"]}次)',
                    'suggestion': f'针对性解决 {error["error_type"]} 错误'
                })
        
        return issues
    
    def _calculate_health_score(self, stats: Dict, success_rate: float, 
                                error_distribution: List[Dict]) -> float:
        """计算任务健康分数 (0-100)"""
        score = 100.0
        
        # 成功率影响 (最多 -40 分)
        if success_rate < 0.95:
            score -= (0.95 - success_rate) * 80
        
        # 执行时间影响 (最多 -20 分)
        if stats['avg_duration']:
            if stats['avg_duration'] > 300:
                score -= 20
            elif stats['avg_duration'] > 120:
                score -= 10
            elif stats['avg_duration'] > 60:
                score -= 5
        
        # Token 消耗影响 (最多 -20 分)
        if stats['avg_tokens']:
            if stats['avg_tokens'] > 50000:
                score -= 20
            elif stats['avg_tokens'] > 20000:
                score -= 10
            elif stats['avg_tokens'] > 10000:
                score -= 5
        
        # 错误分布影响 (最多 -20 分)
        total_errors = sum(e['count'] for e in error_distribution)
        if total_errors > 10:
            score -= 20
        elif total_errors > 5:
            score -= 10
        elif total_errors > 2:
            score -= 5
        
        return max(0, min(100, score))
    
    def _generate_overall_analysis(self, task_analyses: Dict[str, Dict]) -> Dict[str, Any]:
        """生成整体分析"""
        if not task_analyses:
            return {'total_tasks': 0}
        
        total_tasks = len(task_analyses)
        total_executions = sum(t['statistics'].get('total_executions', 0) or 0 for t in task_analyses.values())
        total_success = sum(t['statistics'].get('success_count', 0) or 0 for t in task_analyses.values())
        avg_success_rate = total_success / total_executions if total_executions > 0 else 0
        
        avg_duration = sum((t['statistics'].get('avg_duration') or 0) for t in task_analyses.values()) / total_tasks
        
        total_tokens = sum((t['statistics'].get('total_tokens') or 0) for t in task_analyses.values())
        
        health_scores = [t['health_score'] for t in task_analyses.values()]
        avg_health_score = sum(health_scores) / len(health_scores)
        
        # 健康任务/问题任务统计
        healthy_tasks = [name for name, t in task_analyses.items() if t['health_score'] >= 80]
        problem_tasks = [name for name, t in task_analyses.items() if t['health_score'] < 60]
        
        return {
            'total_tasks': total_tasks,
            'total_executions': total_executions,
            'overall_success_rate': avg_success_rate,
            'avg_duration_seconds': avg_duration,
            'total_tokens_consumed': total_tokens,
            'avg_health_score': avg_health_score,
            'healthy_tasks': healthy_tasks,
            'problem_tasks': problem_tasks,
            'health_distribution': {
                'excellent': len([t for t in task_analyses.values() if t['health_score'] >= 90]),
                'good': len([t for t in task_analyses.values() if 80 <= t['health_score'] < 90]),
                'fair': len([t for t in task_analyses.values() if 60 <= t['health_score'] < 80]),
                'poor': len([t for t in task_analyses.values() if t['health_score'] < 60])
            }
        }
    
    def _generate_recommendations(self, task_analyses: Dict[str, Dict], 
                                  overall: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []
        
        # P0: 问题任务优先处理
        for task_name in overall.get('problem_tasks', []):
            task = task_analyses[task_name]
            recommendations.append({
                'priority': 'P0',
                'category': 'task_optimization',
                'task': task_name,
                'title': f'优化问题任务：{task_name}',
                'description': f'健康分数 {task["health_score"]:.1f}，存在 {len(task["issues"])} 个问题',
                'issues': task['issues'],
                'estimated_impact': 'high',
                'estimated_effort': 'medium'
            })
        
        # P1: 成功率低的任务
        for task_name, task in task_analyses.items():
            if task['success_rate'] < 0.9 and task_name not in overall.get('problem_tasks', []):
                recommendations.append({
                    'priority': 'P1',
                    'category': 'reliability',
                    'task': task_name,
                    'title': f'提升任务可靠性：{task_name}',
                    'description': f'成功率仅 {task["success_rate"]*100:.1f}%',
                    'issues': [i for i in task['issues'] if 'success_rate' in i['type']],
                    'estimated_impact': 'high',
                    'estimated_effort': 'medium'
                })
        
        # P2: 性能优化
        for task_name, task in task_analyses.items():
            if task['statistics']['avg_duration'] and task['statistics']['avg_duration'] > 120:
                if task_name not in [r['task'] for r in recommendations]:
                    recommendations.append({
                        'priority': 'P2',
                        'category': 'performance',
                        'task': task_name,
                        'title': f'优化任务性能：{task_name}',
                        'description': f'平均耗时 {task["statistics"]["avg_duration"]:.1f}秒',
                        'issues': [i for i in task['issues'] if 'duration' in i['type']],
                        'estimated_impact': 'medium',
                        'estimated_effort': 'medium'
                    })
        
        # P3: 整体优化建议
        if overall.get('overall_success_rate', 1.0) < 0.95:
            recommendations.append({
                'priority': 'P3',
                'category': 'system_wide',
                'title': '提升整体任务成功率',
                'description': f'当前整体成功率 {overall.get("overall_success_rate", 0)*100:.1f}%，目标 95%',
                'estimated_impact': 'high',
                'estimated_effort': 'high'
            })
        
        if overall.get('avg_health_score', 100) < 80:
            recommendations.append({
                'priority': 'P3',
                'category': 'system_wide',
                'title': '提升整体任务健康度',
                'description': f'当前平均健康分数 {overall.get("avg_health_score", 100):.1f}，目标 80+',
                'estimated_impact': 'high',
                'estimated_effort': 'high'
            })
        
        return sorted(recommendations, key=lambda x: {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}[x['priority']])
    
    def get_task_health_report(self, task_name: str = None) -> str:
        """生成任务健康报告 (Markdown 格式)"""
        if task_name:
            analysis = self._analyze_single_task(task_name)
            return self._format_single_task_report(task_name, analysis)
        else:
            full_analysis = self.analyze_all_tasks()
            return self._format_full_report(full_analysis)
    
    def _format_single_task_report(self, task_name: str, analysis: Dict) -> str:
        """格式化单个任务报告"""
        report = f"""# 任务健康报告：{task_name}

**分析日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 健康评分

**健康分数**: {analysis['health_score']:.1f}/100

"""
        
        if analysis['health_score'] >= 90:
            report += "✅ **状态**: 优秀\n"
        elif analysis['health_score'] >= 80:
            report += "✅ **状态**: 良好\n"
        elif analysis['health_score'] >= 60:
            report += "⚠️ **状态**: 一般\n"
        else:
            report += "❌ **状态**: 较差\n"
        
        report += f"""
---

## 📈 统计数据 (最近 30 天)

| 指标 | 数值 |
|------|------|
| 执行次数 | {analysis['statistics']['total_executions']} |
| 成功率 | {analysis['success_rate']*100:.1f}% |
| 平均耗时 | {analysis['statistics']['avg_duration']:.1f}秒 |
| 最短耗时 | {analysis['statistics']['min_duration']:.1f}秒 |
| 最长耗时 | {analysis['statistics']['max_duration']:.1f}秒 |
| 平均 Token | {analysis['statistics']['avg_tokens']:.0f} |
| 总 Token | {analysis['statistics']['total_tokens']:.0f} |

---

## ⚠️ 问题列表

"""
        
        if analysis['issues']:
            for issue in analysis['issues']:
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(issue['severity'], '⚪')
                report += f"- {severity_icon} **{issue['type']}**: {issue['description']}\n"
                report += f"  - 建议：{issue['suggestion']}\n"
        else:
            report += "✅ 无重大问题\n"
        
        return report
    
    def _format_full_report(self, analysis: Dict) -> str:
        """格式化完整报告"""
        overall = analysis['overall']
        
        report = f"""# 任务性能分析报告

**分析日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 整体概况

| 指标 | 数值 |
|------|------|
| 总任务数 | {overall['total_tasks']} |
| 总执行次数 | {overall['total_executions']} |
| 整体成功率 | {overall['overall_success_rate']*100:.1f}% |
| 平均耗时 | {overall['avg_duration_seconds']:.1f}秒 |
| 总 Token 消耗 | {overall['total_tokens_consumed']:.0f} |
| 平均健康分数 | {overall['avg_health_score']:.1f} |

---

## 📈 健康分布

| 等级 | 数量 | 描述 |
|------|------|------|
| 优秀 (90+) | {overall['health_distribution']['excellent']} | 无需优化 |
| 良好 (80-89) | {overall['health_distribution']['good']} | 小幅改进 |
| 一般 (60-79) | {overall['health_distribution']['fair']} | 需要改进 |
| 较差 (<60) | {overall['health_distribution']['poor']} | 优先优化 |

---

## ✅ 健康任务

"""
        
        if overall['healthy_tasks']:
            for task in overall['healthy_tasks'][:10]:
                health = analysis['tasks'][task]['health_score']
                report += f"- {task}: {health:.1f}分\n"
        else:
            report += "暂无健康任务\n"
        
        report += f"""
---

## ⚠️ 问题任务

"""
        
        if overall['problem_tasks']:
            for task in overall['problem_tasks']:
                health = analysis['tasks'][task]['health_score']
                issues = analysis['tasks'][task]['issues']
                report += f"### {task} ({health:.1f}分)\n"
                for issue in issues[:3]:
                    report += f"- {issue['description']}\n"
                report += "\n"
        else:
            report += "✅ 无问题任务\n"
        
        report += f"""
---

## 🎯 优化建议

"""
        
        for rec in analysis['recommendations'][:10]:
            priority_icon = {'P0': '🔴', 'P1': '🟠', 'P2': '🟡', 'P3': '🟢'}.get(rec['priority'], '⚪')
            report += f"### {priority_icon} [{rec['priority']}] {rec['title']}\n"
            report += f"{rec['description']}\n\n"
        
        return report


if __name__ == "__main__":
    analyzer = TaskPerformanceAnalyzer()
    
    # 生成完整报告
    report = analyzer.get_task_health_report()
    print(report)
