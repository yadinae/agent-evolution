"""
Agent Evolution - Basic Usage Examples

This file demonstrates basic usage of the Agent Evolution system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from task_analyzer import TaskPerformanceAnalyzer
from skill_analyzer import SkillQualityAnalyzer


def example_1_task_analysis():
    """Example 1: Basic Task Performance Analysis"""
    print("=" * 60)
    print("Example 1: Task Performance Analysis")
    print("=" * 60)
    
    analyzer = TaskPerformanceAnalyzer()
    
    # Analyze all tasks
    analysis = analyzer.analyze_all_tasks()
    
    print(f"\n📊 Task Overview:")
    print(f"  Total Tasks: {analysis['total_tasks']}")
    print(f"  Successful: {analysis['successful_tasks']}")
    print(f"  Failed: {analysis['failed_tasks']}")
    print(f"  Success Rate: {analysis['avg_success_rate']:.2%}")
    
    print(f"\n⏱️  Performance Metrics:")
    print(f"  Average Duration: {analysis['avg_duration']:.2f}s")
    print(f"  Total Token Usage: {analysis['total_tokens']:,}")
    
    print(f"\n💚 Health Score: {analysis['health_score']}/100")
    
    # Get recommendations
    recommendations = analyzer.get_recommendations()
    if recommendations:
        print(f"\n💡 Top Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. [{rec['priority']}] {rec['title']}")
    
    print()


def example_2_skill_quality():
    """Example 2: Skill Quality Assessment"""
    print("=" * 60)
    print("Example 2: Skill Quality Assessment")
    print("=" * 60)
    
    analyzer = SkillQualityAnalyzer()
    
    # Analyze skill library
    analysis = analyzer.analyze_skill_library()
    
    print(f"\n📚 Skill Library Overview:")
    print(f"  Total Skills: {analysis['total_skills']}")
    print(f"  Active Skills: {analysis['active_skills']}")
    print(f"  Unused Skills: {analysis['unused_skills']}")
    
    # Get grade distribution
    report = analyzer.get_skill_library_report()
    print(f"\n📈 Grade Distribution:")
    for grade in ['A', 'B', 'C', 'D']:
        count = report['grade_distribution'].get(grade, 0)
        percentage = (count / analysis['total_skills'] * 100) if analysis['total_skills'] > 0 else 0
        print(f"  Grade {grade}: {count} ({percentage:.1f}%)")
    
    print(f"\n💚 Overall Health Score: {report['overall_health_score']}/100")
    
    # Show unhealthy skills
    if report['unhealthy_skills']:
        print(f"\n⚠️  Unhealthy Skills:")
        for skill in report['unhealthy_skills'][:5]:
            print(f"  - {skill['skill_name']} (Score: {skill['health_score']}/100)")
    
    print()


def example_3_integration():
    """Example 3: Integrated Analysis"""
    print("=" * 60)
    print("Example 3: Integrated Analysis")
    print("=" * 60)
    
    # Task analysis
    task_analyzer = TaskPerformanceAnalyzer()
    task_analysis = task_analyzer.analyze_all_tasks()
    
    # Skill analysis
    skill_analyzer = SkillQualityAnalyzer()
    skill_analysis = skill_analyzer.analyze_skill_library()
    
    print(f"\n🎯 Integrated Insights:")
    print(f"  Task Health: {task_analysis['health_score']}/100")
    print(f"  Skill Health: {skill_analysis['overall_health_score']}/100")
    
    # Combined recommendations
    all_recommendations = []
    all_recommendations.extend(task_analyzer.get_recommendations())
    all_recommendations.extend(skill_analyzer.get_recommendations())
    
    # Sort by priority
    priority_order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
    all_recommendations.sort(key=lambda x: priority_order.get(x['priority'], 99))
    
    print(f"\n📋 Combined Recommendations (Top 5):")
    for i, rec in enumerate(all_recommendations[:5], 1):
        print(f"  {i}. [{rec['priority']}] {rec['title']}")
        print(f"     Expected Benefit: {rec['expected_benefit']}")
        print(f"     Implementation Cost: {rec['implementation_cost']}")
    
    print()


def main():
    """Run all examples"""
    print("\n🧬 Agent Evolution - Usage Examples\n")
    
    try:
        example_1_task_analysis()
    except Exception as e:
        print(f"Error in Example 1: {e}\n")
    
    try:
        example_2_skill_quality()
    except Exception as e:
        print(f"Error in Example 2: {e}\n")
    
    try:
        example_3_integration()
    except Exception as e:
        print(f"Error in Example 3: {e}\n")
    
    print("✅ Examples completed!")


if __name__ == "__main__":
    main()
