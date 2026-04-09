#!/usr/bin/env python3
"""
技能质量分析器

功能:
- 读取技能质量评估结果
- 分析技能库健康状况
- 识别技能缺口
- 生成技能创建/优化建议

用法:
    from skill_analyzer import SkillQualityAnalyzer
    
    analyzer = SkillQualityAnalyzer()
    analysis = analyzer.analyze_skill_library()
    print(analysis)
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
import json


class SkillQualityAnalyzer:
    """技能质量分析器"""
    
    def __init__(self,
                 quality_db: str = "/home/admin/.nanobot/workspace/skill-quality.db",
                 analytics_db: str = "/home/admin/.nanobot/workspace/skills/skill-analytics/skill-analytics.db"):
        self.quality_db = Path(quality_db)
        self.analytics_db = Path(analytics_db)
    
    def analyze_skill_library(self) -> Dict[str, Any]:
        """分析整个技能库"""
        if not self.quality_db.exists():
            return {'error': 'Quality database not found'}
        
        # 获取最新评估数据
        latest_summary = self._get_latest_summary()
        
        if not latest_summary:
            return {'error': 'No evaluation data found'}
        
        # 获取技能详情
        skill_details = self._get_all_skill_details()
        
        # 分析技能库健康状况
        health_analysis = self._analyze_library_health(skill_details)
        
        # 识别技能缺口
        skill_gaps = self._identify_skill_gaps(skill_details, health_analysis)
        
        # 生成优化建议
        recommendations = self._generate_recommendations(skill_details, health_analysis, skill_gaps)
        
        return {
            'analysis_date': datetime.now().isoformat(),
            'summary': latest_summary,
            'health_analysis': health_analysis,
            'skill_details': skill_details,
            'skill_gaps': skill_gaps,
            'recommendations': recommendations
        }
    
    def _get_latest_summary(self) -> Optional[Dict[str, Any]]:
        """获取最新评估汇总"""
        conn = sqlite3.connect(self.quality_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM quality_evaluations_summary
            ORDER BY evaluation_date DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def _get_all_skill_details(self) -> List[Dict[str, Any]]:
        """获取所有技能详情"""
        conn = sqlite3.connect(self.quality_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.*,
                   (SELECT COUNT(*) FROM skill_issues i 
                    WHERE i.skill_name = e.skill_name 
                    AND i.evaluation_id = e.id) as issue_count,
                   (SELECT COUNT(*) FROM skill_recommendations r 
                    WHERE r.skill_name = e.skill_name 
                    AND r.evaluation_id = e.id) as rec_count
            FROM skill_evaluations e
            WHERE e.evaluation_date = (SELECT MAX(evaluation_date) FROM skill_evaluations)
            ORDER BY e.total_score DESC
        """)
        
        skills = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        # 获取使用频率数据
        if self.analytics_db.exists():
            self._enrich_with_usage_data(skills)
        
        return skills
    
    def _enrich_with_usage_data(self, skills: List[Dict]):
        """补充使用频率数据"""
        conn = sqlite3.connect(self.analytics_db)
        cursor = conn.cursor()
        
        for skill in skills:
            cursor.execute("""
                SELECT COUNT(*) as calls_7d
                FROM skill_executions
                WHERE skill_name = ?
                AND timestamp >= datetime('now', '-7 days')
            """, (skill['skill_name'],))
            
            result = cursor.fetchone()
            skill['calls_7d'] = result[0] if result else 0
        
        conn.close()
    
    def _analyze_library_health(self, skill_details: List[Dict]) -> Dict[str, Any]:
        """分析技能库健康状况"""
        if not skill_details:
            return {}
        
        total_skills = len(skill_details)
        
        # 等级分布
        grade_distribution = defaultdict(int)
        for skill in skill_details:
            grade_distribution[skill['grade']] += 1
        
        # 分数分布
        scores = [skill['total_score'] for skill in skill_details]
        avg_score = sum(scores) / len(scores)
        
        # 各维度平均分
        avg_functionality = sum(s['functionality_score'] for s in skill_details) / total_skills
        avg_performance = sum(s['performance_score'] for s in skill_details) / total_skills
        avg_usage = sum(s['usage_score'] for s in skill_details) / total_skills
        avg_code_quality = sum(s['code_quality_score'] for s in skill_details) / total_skills
        avg_documentation = sum(s['documentation_score'] for s in skill_details) / total_skills
        
        # 问题统计
        total_issues = sum(s['issue_count'] for s in skill_details)
        skills_with_issues = [s for s in skill_details if s['issue_count'] > 0]
        
        # 低使用率技能
        low_usage_skills = [s for s in skill_details if s.get('calls_7d', 0) == 0]
        
        # 高质量技能
        high_quality_skills = [s for s in skill_details if s['grade'] == 'A']
        
        return {
            'total_skills': total_skills,
            'average_score': avg_score,
            'grade_distribution': dict(grade_distribution),
            'dimension_averages': {
                'functionality': avg_functionality,
                'performance': avg_performance,
                'usage': avg_usage,
                'code_quality': avg_code_quality,
                'documentation': avg_documentation
            },
            'total_issues': total_issues,
            'skills_with_issues': len(skills_with_issues),
            'low_usage_skills': len(low_usage_skills),
            'high_quality_skills': len(high_quality_skills),
            'health_ratio': {
                'healthy': grade_distribution.get('A', 0) + grade_distribution.get('B', 0),
                'needs_improvement': grade_distribution.get('C', 0),
                'problematic': grade_distribution.get('D', 0)
            }
        }
    
    def _identify_skill_gaps(self, skill_details: List[Dict], 
                            health_analysis: Dict) -> List[Dict[str, Any]]:
        """识别技能缺口"""
        gaps = []
        
        # 1. D 级技能需要重构/删除
        d_grade_skills = [s for s in skill_details if s['grade'] == 'D']
        if d_grade_skills:
            gaps.append({
                'type': 'quality_gap',
                'severity': 'high',
                'title': f'{len(d_grade_skills)} 个 D 级技能需要处理',
                'description': '这些技能质量不达标，需要重构或删除',
                'skills': [s['skill_name'] for s in d_grade_skills],
                'recommendation': '优先重构高使用率的 D 级技能，删除低使用率的'
            })
        
        # 2. 零使用率技能
        zero_usage = [s for s in skill_details if s.get('calls_7d', 0) == 0]
        if zero_usage:
            gaps.append({
                'type': 'usage_gap',
                'severity': 'medium',
                'title': f'{len(zero_usage)} 个技能零使用率',
                'description': '这些技能最近 7 天没有被使用',
                'skills': [s['skill_name'] for s in zero_usage],
                'recommendation': '检查是否有替代技能，或考虑删除'
            })
        
        # 3. 文档质量差的技能
        poor_docs = [s for s in skill_details if s['documentation_score'] < 5]
        if poor_docs:
            gaps.append({
                'type': 'documentation_gap',
                'severity': 'medium',
                'title': f'{len(poor_docs)} 个技能文档质量差',
                'description': '文档评分低于 5 分 (满分 10 分)',
                'skills': [s['skill_name'] for s in poor_docs],
                'recommendation': '补充使用说明和示例'
            })
        
        # 4. 性能差的技能
        poor_performance = [s for s in skill_details if s['performance_score'] < 12]
        if poor_performance:
            gaps.append({
                'type': 'performance_gap',
                'severity': 'medium',
                'title': f'{len(poor_performance)} 个技能性能差',
                'description': '性能评分低于 12 分 (满分 25 分)',
                'skills': [s['skill_name'] for s in poor_performance],
                'recommendation': '优化执行逻辑，减少耗时'
            })
        
        # 5. 代码质量差的技能
        poor_code = [s for s in skill_details if s['code_quality_score'] < 7]
        if poor_code:
            gaps.append({
                'type': 'code_quality_gap',
                'severity': 'high',
                'title': f'{len(poor_code)} 个技能代码质量差',
                'description': '代码质量评分低于 7 分 (满分 15 分)',
                'skills': [s['skill_name'] for s in poor_code],
                'recommendation': '重构代码，添加注释，修复安全问题'
            })
        
        # 6. 高频但低质量技能 (优先优化)
        high_usage_low_quality = [s for s in skill_details 
                                   if s.get('calls_7d', 0) > 10 and s['grade'] in ['C', 'D']]
        if high_usage_low_quality:
            gaps.append({
                'type': 'critical_gap',
                'severity': 'critical',
                'title': f'{len(high_usage_low_quality)} 个高频低质技能',
                'description': '使用频率高但质量差，影响用户体验',
                'skills': [s['skill_name'] for s in high_usage_low_quality],
                'recommendation': '立即优化，这些技能影响面广'
            })
        
        return gaps
    
    def _generate_recommendations(self, skill_details: List[Dict],
                                  health_analysis: Dict,
                                  skill_gaps: List[Dict]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []
        
        # P0: 关键缺口
        critical_gaps = [g for g in skill_gaps if g['severity'] == 'critical']
        for gap in critical_gaps:
            recommendations.append({
                'priority': 'P0',
                'category': 'critical_optimization',
                'title': gap['title'],
                'description': gap['description'],
                'skills': gap['skills'],
                'estimated_impact': 'critical',
                'estimated_effort': 'high'
            })
        
        # P1: 高严重度缺口
        high_gaps = [g for g in skill_gaps if g['severity'] == 'high']
        for gap in high_gaps:
            recommendations.append({
                'priority': 'P1',
                'category': 'quality_improvement',
                'title': gap['title'],
                'description': gap['description'],
                'skills': gap['skills'],
                'estimated_impact': 'high',
                'estimated_effort': 'medium'
            })
        
        # P2: 中等严重度缺口
        medium_gaps = [g for g in skill_gaps if g['severity'] == 'medium']
        for gap in medium_gaps:
            recommendations.append({
                'priority': 'P2',
                'category': 'optimization',
                'title': gap['title'],
                'description': gap['description'],
                'skills': gap['skills'],
                'estimated_impact': 'medium',
                'estimated_effort': 'low'
            })
        
        # P3: 整体优化建议
        if health_analysis['average_score'] < 75:
            recommendations.append({
                'priority': 'P3',
                'category': 'system_wide',
                'title': '提升整体技能质量',
                'description': f'当前平均分 {health_analysis["average_score"]:.1f}，目标 75+',
                'estimated_impact': 'high',
                'estimated_effort': 'high'
            })
        
        if health_analysis['health_ratio']['problematic'] > 0:
            problematic_ratio = health_analysis['health_ratio']['problematic'] / health_analysis['total_skills']
            if problematic_ratio > 0.05:  # 超过 5%
                recommendations.append({
                    'priority': 'P3',
                    'category': 'cleanup',
                    'title': '清理问题技能',
                    'description': f'{problematic_ratio*100:.1f}% 的技能为 D 级，建议清理',
                    'estimated_impact': 'medium',
                    'estimated_effort': 'medium'
                })
        
        # 技能创建建议 (基于使用数据)
        if self.analytics_db.exists():
            creation_suggestions = self._suggest_new_skills()
            recommendations.extend(creation_suggestions)
        
        return sorted(recommendations, key=lambda x: {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}[x['priority']])
    
    def _suggest_new_skills(self) -> List[Dict[str, Any]]:
        """建议创建新技能"""
        suggestions = []
        
        # 分析高频错误类型，建议创建专门处理技能
        if self.analytics_db.exists():
            conn = sqlite3.connect(self.analytics_db)
            cursor = conn.cursor()
            
            # 查找频繁失败的操作模式
            cursor.execute("""
                SELECT skill_name, COUNT(*) as failure_count
                FROM skill_executions
                WHERE status = 'failure'
                AND timestamp >= datetime('now', '-30 days')
                GROUP BY skill_name
                HAVING failure_count >= 5
                ORDER BY failure_count DESC
                LIMIT 5
            """)
            
            problematic_skills = cursor.fetchall()
            conn.close()
            
            if problematic_skills:
                suggestions.append({
                    'priority': 'P2',
                    'category': 'new_skill',
                    'title': '创建错误处理增强技能',
                    'description': f'针对 {len(problematic_skills)} 个频繁失败的技能创建专用错误处理技能',
                    'estimated_impact': 'medium',
                    'estimated_effort': 'medium'
                })
        
        return suggestions
    
    def get_skill_library_report(self) -> str:
        """生成技能库健康报告 (Markdown 格式)"""
        analysis = self.analyze_skill_library()
        
        if 'error' in analysis:
            return f"# 技能库健康报告\n\n❌ {analysis['error']}\n"
        
        summary = analysis['summary']
        health = analysis['health_analysis']
        gaps = analysis['skill_gaps']
        recommendations = analysis['recommendations']
        
        report = f"""# 技能库健康报告

**分析日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 整体概况

| 指标 | 数值 |
|------|------|
| 总技能数 | {health['total_skills']} |
| 平均分数 | {health['average_score']:.1f} |
| 问题总数 | {health['total_issues']} |
| 高质量技能 | {health['high_quality_skills']} |
| 零使用率技能 | {health['low_usage_skills']} |

---

## 📈 等级分布

| 等级 | 数量 | 占比 |
|------|------|------|
| A (优秀) | {health['grade_distribution'].get('A', 0)} | {health['grade_distribution'].get('A', 0)/health['total_skills']*100:.1f}% |
| B (良好) | {health['grade_distribution'].get('B', 0)} | {health['grade_distribution'].get('B', 0)/health['total_skills']*100:.1f}% |
| C (合格) | {health['grade_distribution'].get('C', 0)} | {health['grade_distribution'].get('C', 0)/health['total_skills']*100:.1f}% |
| D (不合格) | {health['grade_distribution'].get('D', 0)} | {health['grade_distribution'].get('D', 0)/health['total_skills']*100:.1f}% |

---

## 📊 维度分析

| 维度 | 平均分 | 满分 | 得分率 |
|------|--------|------|--------|
| 功能完整性 | {health['dimension_averages']['functionality']:.1f} | 30 | {health['dimension_averages']['functionality']/30*100:.1f}% |
| 性能表现 | {health['dimension_averages']['performance']:.1f} | 25 | {health['dimension_averages']['performance']/25*100:.1f}% |
| 使用频率 | {health['dimension_averages']['usage']:.1f} | 20 | {health['dimension_averages']['usage']/20*100:.1f}% |
| 代码质量 | {health['dimension_averages']['code_quality']:.1f} | 15 | {health['dimension_averages']['code_quality']/15*100:.1f}% |
| 文档质量 | {health['dimension_averages']['documentation']:.1f} | 10 | {health['dimension_averages']['documentation']/10*100:.1f}% |

---

## ⚠️ 技能缺口

"""
        
        if gaps:
            for gap in gaps:
                severity_icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(gap['severity'], '⚪')
                report += f"### {severity_icon} [{gap['severity'].upper()}] {gap['title']}\n"
                report += f"{gap['description']}\n"
                report += f"**建议**: {gap['recommendation']}\n\n"
        else:
            report += "✅ 无明显技能缺口\n\n"
        
        report += f"""
---

## 🎯 优化建议

"""
        
        if recommendations:
            for rec in recommendations[:10]:
                priority_icon = {'P0': '🔴', 'P1': '🟠', 'P2': '🟡', 'P3': '🟢'}.get(rec['priority'], '⚪')
                report += f"### {priority_icon} [{rec['priority']}] {rec['title']}\n"
                report += f"{rec['description']}\n\n"
        else:
            report += "✅ 无需特别优化\n"
        
        return report


if __name__ == "__main__":
    analyzer = SkillQualityAnalyzer()
    
    # 生成报告
    report = analyzer.get_skill_library_report()
    print(report)
