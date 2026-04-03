"""
Agent Evolution - Test Suite

Run tests with: pytest tests/ -v
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_imports():
    """Test that all core modules can be imported"""
    from task_analyzer import TaskPerformanceAnalyzer
    from skill_analyzer import SkillQualityAnalyzer
    
    assert TaskPerformanceAnalyzer is not None
    assert SkillQualityAnalyzer is not None


def test_task_analyzer_initialization():
    """Test TaskPerformanceAnalyzer initialization"""
    from task_analyzer import TaskPerformanceAnalyzer
    
    analyzer = TaskPerformanceAnalyzer()
    assert analyzer is not None


def test_skill_analyzer_initialization():
    """Test SkillQualityAnalyzer initialization"""
    from skill_analyzer import SkillQualityAnalyzer
    
    analyzer = SkillQualityAnalyzer()
    assert analyzer is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
