"""
Tests for TaskPerformanceAnalyzer
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from task_analyzer import TaskPerformanceAnalyzer


class TestTaskPerformanceAnalyzer:
    """Test cases for TaskPerformanceAnalyzer"""
    
    @pytest.fixture
    def sample_db(self):
        """Create a sample database for testing"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create execution_stages table
        cursor.execute('''
            CREATE TABLE execution_stages (
                id INTEGER PRIMARY KEY,
                task_name TEXT,
                stage TEXT,
                status TEXT,
                duration REAL,
                tokens_used INTEGER,
                timestamp TEXT
            )
        ''')
        
        # Insert sample data
        sample_data = [
            ('task1', 'planning', 'success', 1.5, 1000, '2026-04-03 10:00:00'),
            ('task1', 'execution', 'success', 2.0, 2000, '2026-04-03 10:01:00'),
            ('task2', 'planning', 'success', 1.0, 800, '2026-04-03 10:02:00'),
            ('task2', 'execution', 'failed', 0.5, 500, '2026-04-03 10:03:00'),
            ('task3', 'planning', 'success', 1.2, 900, '2026-04-03 10:04:00'),
            ('task3', 'execution', 'success', 2.5, 2500, '2026-04-03 10:05:00'),
        ]
        
        cursor.executemany(
            'INSERT INTO execution_stages (task_name, stage, status, duration, tokens_used, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
            sample_data
        )
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink()
    
    def test_initialization(self, sample_db):
        """Test analyzer initialization"""
        analyzer = TaskPerformanceAnalyzer(db_path=sample_db)
        assert analyzer is not None
    
    def test_analyze_all_tasks(self, sample_db):
        """Test task analysis"""
        analyzer = TaskPerformanceAnalyzer(db_path=sample_db)
        analysis = analyzer.analyze_all_tasks()
        
        assert 'total_tasks' in analysis
        assert 'successful_tasks' in analysis
        assert 'failed_tasks' in analysis
        assert 'avg_success_rate' in analysis
        assert 'health_score' in analysis
        
        assert analysis['total_tasks'] == 3
        assert analysis['successful_tasks'] == 2
        assert analysis['failed_tasks'] == 1
    
    def test_get_recommendations(self, sample_db):
        """Test recommendation generation"""
        analyzer = TaskPerformanceAnalyzer(db_path=sample_db)
        recommendations = analyzer.get_recommendations()
        
        assert isinstance(recommendations, list)
        
        if recommendations:
            rec = recommendations[0]
            assert 'priority' in rec
            assert 'title' in rec
            assert 'description' in rec


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
