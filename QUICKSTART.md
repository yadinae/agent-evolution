# Agent Evolution - 快速参考指南

## 🚀 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/yadadinae/agent-evolution.git
cd agent-evolution

# 运行安装脚本
bash scripts/setup.sh

# 或手动安装
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 配置

```bash
# 复制配置模板
cp config/.env.example config/.env

# 编辑配置文件
vim config/.env
```

**必需配置**:
```ini
FEISHU_APP_ID=your_app_id
FEISHU_CHANNEL_ID=your_channel_id
TASK_MONITORING_DB=data/task-monitoring.db
SKILL_QUALITY_DB=data/skill-quality.db
```

### 3. 运行

```bash
# 健康检查
python src/evolve_analysis.py --health-check

# 生成进化报告
python src/evolve_analysis.py --generate-report

# 查看任务分析
python src/task_analyzer.py --analyze

# 查看技能质量
python src/skill_analyzer.py --report
```

---

## 📋 常用命令

### 任务分析

```bash
# 分析所有任务
python src/task_analyzer.py --analyze-all

# 获取健康报告
python src/task_analyzer.py --health-report

# 查看优化建议
python src/task_analyzer.py --recommendations

# 导出 JSON 报告
python src/task_analyzer.py --export-json report.json
```

### 技能分析

```bash
# 分析技能库
python src/skill_analyzer.py --analyze-library

# 查看技能排行榜
python src/skill_analyzer.py --top-skills --limit 10

# 查看待优化技能
python src/skill_analyzer.py --unhealthy-skills

# 识别技能缺口
python src/skill_analyzer.py --skill-gaps
```

### 进化引擎

```bash
# 完整进化分析
python src/evolve_analysis.py --full-analysis

# 生成进化报告
python src/evolve_analysis.py --report

# 发送飞书通知
python src/evolve_analysis.py --notify

# 定时执行 (cron)
0 3 * * * /path/to/evolve_analysis.py --auto
```

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_task_analyzer.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看覆盖率
open htmlcov/index.html
```

---

## 📊 核心 API

### TaskPerformanceAnalyzer

```python
from src.task_analyzer import TaskPerformanceAnalyzer

analyzer = TaskPerformanceAnalyzer(db_path="data/task-monitoring.db")

# 分析所有任务
analysis = analyzer.analyze_all_tasks()
print(f"健康分数：{analysis['health_score']}/100")

# 获取建议
recommendations = analyzer.get_recommendations()
for rec in recommendations:
    print(f"[{rec['priority']}] {rec['title']}")
```

### SkillQualityAnalyzer

```python
from src.skill_analyzer import SkillQualityAnalyzer

analyzer = SkillQualityAnalyzer(db_path="data/skill-quality.db")

# 分析技能库
analysis = analyzer.analyze_skill_library()
print(f"总技能数：{analysis['total_skills']}")

# 获取等级分布
report = analyzer.get_skill_library_report()
for grade, count in report['grade_distribution'].items():
    print(f"{grade}级：{count}个")
```

---

## 📁 项目结构速查

```
agent-evolution/
├── src/              # 源代码
│   ├── evolve_analysis.py
│   ├── task_analyzer.py
│   ├── skill_analyzer.py
│   └── ...
├── tests/            # 测试
├── examples/         # 示例
├── config/           # 配置
├── data/             # 数据库
├── docs/             # 文档
└── scripts/          # 脚本
```

---

## 🔧 故障排查

### 数据库连接失败

```bash
# 检查数据库文件
ls -la data/*.db

# 检查数据库完整性
python -c "import sqlite3; conn = sqlite3.connect('data/task-monitoring.db'); print('OK')"
```

### 飞书通知失败

```bash
# 检查环境变量
echo $FEISHU_APP_ID
echo $FEISHU_CHANNEL_ID

# 测试连接
python -c "from src.feishu_reporter import FeishuReporter; r = FeishuReporter(); print('OK')"
```

### 性能下降

```bash
# 运行性能测试
pytest tests/test_performance.py -v

# 检查数据库大小
du -h data/*.db

# 清理旧数据
python scripts/cleanup.py --days 30
```

---

## 📚 文档链接

- **README.md** - 完整项目说明
- **CONTRIBUTING.md** - 贡献指南
- **CHANGELOG.md** - 变更日志
- **docs/** - 技术文档
- **examples/** - 代码示例

---

## 💡 使用技巧

### 1. 自定义分析

```python
# 自定义时间范围
analysis = analyzer.analyze_tasks(
    start_date="2026-04-01",
    end_date="2026-04-03"
)

# 自定义指标
metrics = analyzer.get_custom_metrics([
    'success_rate',
    'avg_duration',
    'token_efficiency'
])
```

### 2. 批量处理

```bash
# 批量分析多个数据库
for db in data/*.db; do
    python src/task_analyzer.py --db $db --output reports/$(basename $db).json
done
```

### 3. 定时任务

```bash
# 添加到 crontab
crontab -e

# 每天 03:00 执行
0 3 * * * cd /path/to/agent-evolution && python src/evolve_analysis.py --auto
```

---

## 🎯 最佳实践

1. **定期备份数据库**
   ```bash
   cp data/task-monitoring.db backups/task-monitoring-$(date +%Y%m%d).db
   ```

2. **监控性能指标**
   ```python
   # 记录历史数据
   analyzer.log_metrics_to_file("metrics.log")
   ```

3. **设置告警阈值**
   ```ini
   # config/alert-thresholds.conf
   warning_health_score = 60
   critical_health_score = 40
   ```

4. **定期清理旧数据**
   ```bash
   python scripts/cleanup.py --days 30 --dry-run
   ```

---

## 📞 获取帮助

- **GitHub Issues**: https://github.com/yadadinae/agent-evolution/issues
- **讨论区**: https://github.com/yadadinae/agent-evolution/discussions
- **Email**: support@studyai.ltd

---

*最后更新：2026-04-03*
