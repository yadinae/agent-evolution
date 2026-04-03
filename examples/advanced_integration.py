"""
Agent Evolution - Advanced Integration Example

This example demonstrates advanced integration patterns including:
- Custom data sources
- Report export
- Webhook notifications
- Scheduled execution
"""

import json
import os
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from task_analyzer import TaskPerformanceAnalyzer
from skill_analyzer import SkillQualityAnalyzer


class AdvancedEvolutionEngine:
    """Advanced Evolution Engine with custom integrations"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.task_analyzer = TaskPerformanceAnalyzer()
        self.skill_analyzer = SkillQualityAnalyzer()
        
    def generate_comprehensive_report(self):
        """Generate comprehensive evolution report"""
        print("🔍 Generating comprehensive report...")
        
        # Analyze tasks
        task_analysis = self.task_analyzer.analyze_all_tasks()
        
        # Analyze skills
        skill_analysis = self.skill_analyzer.analyze_skill_library()
        
        # Generate recommendations
        recommendations = self._merge_recommendations()
        
        # Build report
        report = {
            "report_id": f"evolution-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "task_health": task_analysis['health_score'],
                "skill_health": skill_analysis['overall_health_score'],
                "overall_health": (task_analysis['health_score'] + skill_analysis['overall_health_score']) / 2,
                "total_recommendations": len(recommendations),
                "critical_issues": len([r for r in recommendations if r['priority'] == 'P0'])
            },
            "task_performance": task_analysis,
            "skill_quality": skill_analysis,
            "recommendations": recommendations,
            "trends": self._calculate_trends(task_analysis, skill_analysis)
        }
        
        return report
    
    def _merge_recommendations(self):
        """Merge and prioritize recommendations from all sources"""
        all_recs = []
        
        # Get task recommendations
        task_recs = self.task_analyzer.get_recommendations()
        all_recs.extend(task_recs)
        
        # Get skill recommendations
        skill_recs = self.skill_analyzer.get_recommendations()
        all_recs.extend(skill_recs)
        
        # Sort by priority
        priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        all_recs.sort(key=lambda x: (priority_order.get(x['priority'], 99), -x.get('impact_score', 0)))
        
        return all_recs
    
    def _calculate_trends(self, task_analysis, skill_analysis):
        """Calculate trends and insights"""
        trends = {
            "task_success_rate_trend": "stable",  # Would calculate from historical data
            "skill_quality_trend": "improving",
            "health_score_trend": "stable"
        }
        return trends
    
    def export_report_json(self, report, output_path):
        """Export report to JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ Report exported to {output_path}")
    
    def export_report_markdown(self, report, output_path):
        """Export report to Markdown"""
        md = []
        md.append("# Agent Evolution Report\n")
        md.append(f"**Generated**: {report['generated_at']}\n")
        md.append(f"**Report ID**: {report['report_id']}\n\n")
        
        # Summary
        md.append("## Summary\n")
        summary = report['summary']
        md.append(f"- **Overall Health**: {summary['overall_health']:.1f}/100")
        md.append(f"- **Task Health**: {summary['task_health']}/100")
        md.append(f"- **Skill Health**: {summary['skill_health']}/100")
        md.append(f"- **Total Recommendations**: {summary['total_recommendations']}")
        md.append(f"- **Critical Issues**: {summary['critical_issues']}\n\n")
        
        # Recommendations
        md.append("## Recommendations\n")
        for i, rec in enumerate(report['recommendations'][:10], 1):
            md.append(f"### {i}. [{rec['priority']}] {rec['title']}\n")
            md.append(f"- **Description**: {rec['description']}")
            md.append(f"- **Expected Benefit**: {rec['expected_benefit']}")
            md.append(f"- **Implementation Cost**: {rec['implementation_cost']}\n")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md))
        print(f"✅ Report exported to {output_path}")
    
    def send_webhook_notification(self, report, webhook_url):
        """Send report to webhook (e.g., Slack, Discord)"""
        import requests
        
        summary = report['summary']
        payload = {
            "text": f"🧬 Agent Evolution Report\n"
                    f"Overall Health: {summary['overall_health']:.1f}/100\n"
                    f"Critical Issues: {summary['critical_issues']}\n"
                    f"Recommendations: {summary['total_recommendations']}"
        }
        
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            print("✅ Webhook notification sent")
        except Exception as e:
            print(f"❌ Failed to send webhook: {e}")


def example_scheduled_execution():
    """Example: Scheduled execution pattern"""
    print("=" * 60)
    print("Example: Scheduled Execution Pattern")
    print("=" * 60)
    
    engine = AdvancedEvolutionEngine()
    
    # Generate report
    report = engine.generate_comprehensive_report()
    
    # Export to different formats
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    engine.export_report_json(report, f"reports/evolution-{timestamp}.json")
    engine.export_report_markdown(report, f"reports/evolution-{timestamp}.md")
    
    # Send notification (if webhook configured)
    webhook_url = os.getenv('EVOLUTION_WEBHOOK_URL')
    if webhook_url:
        engine.send_webhook_notification(report, webhook_url)
    
    print()


def example_custom_data_source():
    """Example: Custom data source integration"""
    print("=" * 60)
    print("Example: Custom Data Source Integration")
    print("=" * 60)
    
    # You can extend the analyzers to work with custom data sources
    # For example, integrating with external monitoring systems
    
    print("Custom data source integration would involve:")
    print("1. Extending TaskPerformanceAnalyzer with custom DB adapter")
    print("2. Implementing data transformation layer")
    print("3. Configuring data source in config/.env")
    print()


def example_ci_cd_integration():
    """Example: CI/CD pipeline integration"""
    print("=" * 60)
    print("Example: CI/CD Pipeline Integration")
    print("=" * 60)
    
    print("Agent Evolution can be integrated into CI/CD pipelines:")
    print("\nGitHub Actions example:")
    print("""
    name: Agent Evolution Check
    on: [push, pull_request]
    
    jobs:
      evolution-check:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v3
          - name: Set up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.11'
          - name: Install dependencies
            run: pip install -r requirements.txt
          - name: Run evolution analysis
            run: python src/evolve_analysis.py --ci-mode
          - name: Upload report
            uses: actions/upload-artifact@v3
            with:
              name: evolution-report
              path: reports/
    """)
    print()


def main():
    """Run all advanced examples"""
    print("\n🧬 Agent Evolution - Advanced Examples\n")
    
    # Create reports directory
    Path("reports").mkdir(exist_ok=True)
    
    try:
        example_scheduled_execution()
    except Exception as e:
        print(f"Error in Scheduled Execution: {e}\n")
    
    try:
        example_custom_data_source()
    except Exception as e:
        print(f"Error in Custom Data Source: {e}\n")
    
    try:
        example_ci_cd_integration()
    except Exception as e:
        print(f"Error in CI/CD Integration: {e}\n")
    
    print("✅ Advanced examples completed!")


if __name__ == "__main__":
    main()
