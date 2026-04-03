"""
Tests for SkillQualityAnalyzer
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from skill_analyzer import SkillQualityAnalyzer


class TestSkillQualityAnalyzer:
    """Test cases for SkillQualityAnalyzer"""
    
    @pytest.fixture
    def sample_db(self):
        """Create a sample database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create quality_evaluations_summary table
        cursor.execute('''
            CREATE TABLE quality_evaluations_summary (
                id INTEGER PRIMARY KEY,
                skill_name TEXT,
                overall_score REAL,
                grade TEXT,
                execution_count INTEGER,
                doc_coverage REAL,
                test_coverage REAL,
                last_evaluated TEXT
            )
        ''')
        
        # Insert sample data
        sample_data = [
            ('skill1', 95.0, 'A', 100, 0.95, 0.90, '2026-04-03'),
            ('skill2', 80.0, 'B', 50, 0.80, 0.75, '2026-04-03'),
            ('skill3', 65.0, 'C', 20, 0.60, 0.50, '2026-04-03'),
            ('skill4', 45.0, 'D', 5, 0.40, 0.30, '2026-04-03'),
            ('skill5', 85.0, 'B', 0, 0.85, 0.80, '2026-04-03'),  # Unused skill
        ]
        
        cursor.executemany(
            '''INSERT INTO quality_evaluations_summary 
               (skill_name, overall_score, grade, execution_count, doc_coverage, test_coverage, last_evaluated) 
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            sample_data
        )
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink()
    
    def test_initialization(self, sample_db):
        """Test analyzer initialization"""
        analyzer = SkillQualityAnalyzer(db_path=sample_db)
        assert analyzer is not None
    
    def test_analyze_skill_library(self, sample_db):
        """Test skill library analysis"""
        analyzer = SkillQualityAnalyzer(db_path=sample_db)
        analysis = analyzer.analyze_skill_library()
        
        assert 'total_skills' in analysis
        assert 'active_skills' in analysis
        assert 'unused_skills' in analysis
        assert 'overall_health_score' in analysis
        
        assert analysis['total_skills'] == 5
        assert analysis['unused_skills'] == 1
    
    def test_get_skill_library_report(self, sample_db):
        """Test skill library report generation"""
        analyzer = SkillQualityAnalyzer(db_path=sample_db)
        report = analyzer.get_skill_library_report()
        
        assert 'grade_distribution' in report
        assert 'overall_health_score' in report
        assert 'unhealthy_skills' in report
        
        grade_dist = report['grade_distribution']
        assert grade_dist.get('A', 0) == 1
        assert grade_dist.get('B', 0) == 2
        assert grade_dist.get('C', 0) == 1
        assert grade_dist.get('D', 0) == 1
    
    def test_identify_skill_gaps(self, sample_db):
        """Test skill gap identification"""
        analyzer = SkillQualityAnalyzer(db_path=sample_db)
        gaps = analyzer.identify_skill_gaps()
        
        assert isinstance(gaps, list)
        
        # Should identify D-grade skills and unused skills
        if gaps:
            gap = gaps[0]
            assert 'skill_name' in gap
            assert 'issue_type' in gap
            assert 'recommendation' in gap


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
