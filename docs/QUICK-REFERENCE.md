# 快速参考指南 ⚡

Agent Evolution 快速参考指南 - 常用命令和操作速查表

---

## 📖 目录

- [快速开始](#快速开始)
- [常用命令](#常用命令)
- [配置管理](#配置管理)
- [监控运维](#监控运维)
- [故障排查](#故障排查)
- [性能优化](#性能优化)
- [API 速查](#api-速查)
- [最佳实践](#最佳实践)

---

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yadinae/agent-evolution.git
cd agent-evolution

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行健康检查

```bash
# 系统健康检查
python src/evolve_analysis.py --health-check

# 生成进化报告
python src/evolve_analysis.py --generate-report

# 查看技能排行榜
python src/skill_analyzer.py --top-skills --limit 10
```

### 配置定时任务

```bash
# 配置 crontab
crontab config/agent-evolution.crontab

# 查看已配置任务
crontab -l
```

---

## 常用命令

### 任务分析

```bash
# 分析所有任务
python src/task_analyzer.py --analyze-all

# 查看任务健康报告
python src/task_analyzer.py --health-report

# 识别性能瓶颈
python src/task_analyzer.py --identify-bottlenecks

# 获取优化建议
python src/task_analyzer.py --recommendations
```

### 技能分析

```bash
# 分析技能库
python src/skill_analyzer.py --analyze-library

# 查看技能质量报告
python src/skill_analyzer.py --quality-report

# 识别技能缺口
python src/skill_analyzer.py --skill-gaps

# 技能排行榜
python src/skill_analyzer.py --top-skills --limit 10 --metric success_rate
```

### 进化分析

```bash
# 生成完整进化报告
python src/evolve_analysis.py --full-report

# 发送飞书通知
python src/evolve_analysis.py --send-notification

# 导出 Markdown 报告
python src/evolve_analysis.py --export-markdown report.md

# 导出 JSON 报告
python src/evolve_analysis.py --export-json report.json
```

---

## 配置管理

### 环境变量

```bash
# .env 文件配置
FEISHU_APP_ID=cli_a90b5d6d8e395bc9
FEISHU_CHANNEL_ID=ou_608260b868adf690d70569214d83cfda

TASK_MONITORING_DB=data/task-monitoring.db
SKILL_QUALITY_DB=data/skill-quality.db
SKILL_ANALYTICS_DB=data/skill-analytics.db

LOG_LEVEL=INFO
LOG_FILE=logs/evolution.log
```

### 告警阈值

```ini
# config/alert-thresholds.conf

[error_thresholds]
critical_error_rate=0.1
warning_error_rate=0.05

[performance_thresholds]
min_success_rate=0.8
max_avg_duration=60.0

[health_thresholds]
critical_health_score=40
warning_health_score=60
```

### 数据库配置

```python
# 数据库连接配置
DATABASE_CONFIG = {
    'task_monitoring': 'data/task-monitoring.db',
    'skill_quality': 'data/skill-quality.db',
    'skill_analytics': 'data/skill-analytics.db'
}

# SQLite 优化配置
PRAGMA_CONFIG = [
    'PRAGMA journal_mode = WAL',
    'PRAGMA synchronous = NORMAL',
    'PRAGMA cache_size = -64000',  # 64MB
    'PRAGMA temp_store = MEMORY'
]
```

---

## 监控运维

### 健康检查

```bash
# 运行完整健康检查
./scripts/health-check.sh

# 检查 Python 环境
./scripts/health-check.sh --python

# 检查数据库
./scripts/health-check.sh --database

# 检查磁盘空间
./scripts/health-check.sh --disk

# 检查内存使用
./scripts/health-check.sh --memory
```

### 性能监控

```bash
# 启动性能监控
./scripts/monitor-performance.sh

# 查看监控仪表板
python scripts/monitor-dashboard.py

# JSON 输出模式
python scripts/monitor-dashboard.py --json

# 持续监控模式
python scripts/monitor-dashboard.py --watch
```

### 错误监控

```bash
# 运行错误监控
./scripts/monitor-errors.sh

# 查看今日错误
./scripts/monitor-errors.sh --today

# 查看严重错误
./scripts/monitor-errors.sh --critical

# 生成错误报告
./scripts/monitor-errors.sh --report
```

### 备份管理

```bash
# 创建备份
./scripts/backup.sh

# 验证备份
./scripts/verify-backup.py backup-20260403-092559.tar.gz

# 恢复备份
./scripts/restore.sh backup-20260403-092559.tar.gz

# 清理旧备份
./scripts/cleanup-backups.py --days 30

# 列出所有备份
./scripts/backup.sh --list
```

---

## 故障排查

### 常见问题速查

#### 问题 1: 数据库连接失败

```bash
# 检查数据库文件
ls -la data/*.db

# 检查数据库完整性
python -c "import sqlite3; conn = sqlite3.connect('data/task-monitoring.db'); print(conn.execute('SELECT 1').fetchone())"

# 修复数据库
sqlite3 data/task-monitoring.db "PRAGMA integrity_check"
```

#### 问题 2: 飞书通知失败

```bash
# 检查环境变量
echo $FEISHU_APP_ID
echo $FEISHU_CHANNEL_ID

# 测试 API 连接
curl -X POST https://open.feishu.cn/open-apis/message/v4/send \
  -H "Authorization: Bearer $FEISHU_TOKEN" \
  -d '{"chat_id":"'$FEISHU_CHANNEL_ID'","msg_type":"text","content":{"text":"test"}}'
```

#### 问题 3: 性能下降

```bash
# 运行性能基准测试
pytest tests/test_performance_benchmark.py -v

# 检查数据库大小
du -h data/*.db

# 清理旧数据
python scripts/cleanup.py --days 30

# 重建索引
sqlite3 data/task-monitoring.db "REINDEX"
```

#### 问题 4: 测试失败

```bash
# 运行特定测试
pytest tests/test_task_analyzer.py::TestTaskAnalyzer::test_analyze_success -v

# 显示详细输出
pytest tests/ -v -s

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看失败详情
pytest tests/ --lf  # 运行上次失败的测试
```

#### 问题 5: 定时任务未执行

```bash
# 检查 crontab 配置
crontab -l

# 检查 cron 服务状态
systemctl status cron  # Linux
sudo launchctl list | grep cron  # macOS

# 查看 cron 日志
grep CRON /var/log/syslog  # Linux
log show --predicate 'process == "cron"' --last 1h  # macOS

# 手动执行脚本
./scripts/evolve.sh
```

### 调试模式

```bash
# 启用调试日志
export LOG_LEVEL=DEBUG

# 运行详细输出
python src/evolve_analysis.py --verbose

# 启用 SQL 日志
export SQLITE_DEBUG=1

# 性能分析
python -m cProfile -o output.prof src/evolve_analysis.py
python -m pstats output.prof
```

---

## 性能优化

### 数据库优化

```sql
-- 创建索引
CREATE INDEX IF NOT EXISTS idx_executions_skill_time 
ON skill_executions(skill_name, start_time);

CREATE INDEX IF NOT EXISTS idx_errors_type_time 
ON error_events(error_type, timestamp);

-- 启用 WAL 模式
PRAGMA journal_mode = WAL;

-- 优化缓存
PRAGMA cache_size = -64000;  -- 64MB

-- 分析表
ANALYZE;
```

### 查询优化

```python
# ✅ 好的查询 (使用索引)
cursor.execute("""
    SELECT * FROM skill_executions
    WHERE skill_name = ? AND start_time > ?
    ORDER BY start_time DESC
    LIMIT 100
""", (skill_name, start_time))

# ❌ 慢查询 (全表扫描)
cursor.execute("""
    SELECT * FROM skill_executions
    WHERE LOWER(skill_name) = LOWER(?)
""", (skill_name,))
```

### 缓存策略

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_analysis_result(analysis_id: str) -> dict:
    """获取分析结果 (带缓存)"""
    return _fetch_from_database(analysis_id)

# 清除缓存
get_analysis_result.cache_clear()
```

### 并发处理

```python
from concurrent.futures import ThreadPoolExecutor

# 使用线程池并行处理
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(analyze_task, task_list))
```

---

## API 速查

### TaskPerformanceAnalyzer

```python
from src.task_analyzer import TaskPerformanceAnalyzer

analyzer = TaskPerformanceAnalyzer()

# 分析所有任务
analysis = analyzer.analyze_all_tasks()

# 获取健康报告
report = analyzer.get_task_health_report()

# 识别瓶颈
bottlenecks = analyzer.identify_bottlenecks()

# 获取建议
recommendations = analyzer.get_recommendations()
```

### SkillQualityAnalyzer

```python
from src.skill_analyzer import SkillQualityAnalyzer

analyzer = SkillQualityAnalyzer()

# 分析技能库
analysis = analyzer.analyze_skill_library()

# 获取技能库报告
report = analyzer.get_skill_library_report()

# 识别技能缺口
gaps = analyzer.identify_skill_gaps()

# 获取不健康技能
unhealthy = analyzer.get_unhealthy_skills()
```

### EvolutionEngine

```python
from src.evolve_analysis import EvolutionEngine

engine = EvolutionEngine()

# 生成进化报告
report = engine.generate_evolution_report()

# 发送飞书通知
engine.send_feishu_notification(report)

# 导出 Markdown
md_report = engine.export_report_markdown()

# 导出 JSON
json_report = engine.export_report_json()
```

---

## 最佳实践

### 代码规范

```python
# ✅ 使用类型注解
def analyze_task(task_id: int) -> dict:
    """分析任务"""
    pass

# ✅ 使用文档字符串
class TaskAnalyzer:
    """任务分析器"""
    pass

# ✅ 使用上下文管理器
with analyzer.track_execution(skill_name):
    # 执行代码
    pass

# ✅ 异常处理
try:
    result = analyzer.analyze(task_id)
except ValueError as e:
    logger.error(f"分析失败：{e}")
    raise
```

### 测试规范

```python
# ✅ 完整的测试
def test_analyze_success(self, sample_task):
    """测试成功分析任务"""
    analyzer = TaskAnalyzer()
    result = analyzer.analyze(sample_task['id'])
    
    assert result['status'] == 'success'
    assert 'metrics' in result
    assert result['metrics']['success_rate'] > 0

# ✅ 异常测试
def test_analyze_invalid_task(self):
    """测试分析无效任务"""
    analyzer = TaskAnalyzer()
    
    with pytest.raises(ValueError):
        analyzer.analyze(-1)
```

### 日志规范

```python
import logging

logger = logging.getLogger(__name__)

# ✅ 好的日志
logger.info(f"开始分析任务 {task_id}")
logger.debug(f"任务数据：{task_data}")
logger.warning(f"任务成功率低于阈值：{success_rate}")
logger.error(f"分析失败：{e}", exc_info=True)

# ❌ 不好的日志
print("开始分析")
print(data)
```

### 配置管理

```python
# ✅ 使用配置文件
import configparser

config = configparser.ConfigParser()
config.read('config/settings.conf')
db_path = config['database']['path']

# ✅ 使用环境变量
import os
db_path = os.getenv('TASK_MONITORING_DB', 'data/task-monitoring.db')

# ❌ 硬编码
db_path = 'data/task-monitoring.db'
```

---

## 快捷键速查

### 命令行快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl + C` | 中断命令 |
| `Ctrl + Z` | 挂起命令 |
| `Ctrl + D` | 退出 shell |
| `Ctrl + R` | 搜索历史命令 |
| `Ctrl + L` | 清屏 |
| `Tab` | 自动补全 |
| `!!` | 重复上一条命令 |
| `!$` | 上一条命令的最后一个参数 |

### Git 快捷键

| 命令 | 功能 |
|------|------|
| `git st` | `git status` (别名) |
| `git co` | `git checkout` (别名) |
| `git br` | `git branch` (别名) |
| `git ci` | `git commit` (别名) |
| `git lg` | `git log --graph` (别名) |

---

## 资源链接

- **GitHub 仓库**: https://github.com/yadinae/agent-evolution
- **问题追踪**: https://github.com/yadinae/agent-evolution/issues
- **完整文档**: docs/
- **架构设计**: docs/AGENT-EVOLUTION-FOUR-LAYERS-ARCHITECTURE.md
- **实施计划**: docs/PHASED-IMPLEMENTATION-PLAN.md
- **API 文档**: docs/API.md
- **贡献指南**: CONTRIBUTING.md

---

*文档版本：1.0.0*  
*创建时间：2026-04-03*  
*最后更新：2026-04-03*
