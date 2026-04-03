# Agent Evolution 🧬

**Agent 自我进化系统** - 基于数据驱动的 AI Agent 能力提升平台

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-131%2B-green.svg)](https://github.com/yadadinae/agent-evolution)
[![Coverage](https://img.shields.io/badge/coverage-95%25-green.svg)](https://github.com/yadadinae/agent-evolution)

---

## 📖 目录

- [简介](#-简介)
- [核心功能](#-核心功能)
- [系统架构](#-系统架构)
- [快速开始](#-快速开始)
- [项目结构](#-项目结构)
- [核心模块](#-核心模块)
- [使用示例](#-使用示例)
- [配置说明](#-配置说明)
- [开发指南](#-开发指南)
- [API 参考](#-api-参考)
- [性能指标](#-性能指标)
- [故障排查](#-故障排查)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 🎯 简介

Agent Evolution 是一个完整的 Agent 自我进化系统，整合了**任务性能监控**、**技能质量评估**、**智能调度引擎**和**数据驱动的进化建议**。

### 核心价值

- 📊 **数据驱动决策** - 所有分析基于真实监控数据
- 🎯 **智能优先级** - P0/P1/P2/P3 四级优先级排序
- 📈 **健康评分系统** - 0-100 分量化 Agent 健康状态
- 🔍 **问题诊断** - 自动识别瓶颈并生成优化建议
- 📝 **可视化报告** - Markdown/JSON 格式报告导出
- 🔔 **主动通知** - 飞书/邮件等多渠道通知

### 适用场景

- AI Agent 性能优化
- 技能库质量管理
- 任务调度策略优化
- 错误模式分析
- 自动化改进建议

---

## 🚀 核心功能

### 1. 任务性能监控 (Task Monitoring)

实时监控任务执行状态，分析成功率、耗时、Token 消耗等关键指标。

```python
from src.task_analyzer import TaskPerformanceAnalyzer

analyzer = TaskPerformanceAnalyzer()
analysis = analyzer.analyze_all_tasks()
print(f"总任务数：{analysis['total_tasks']}")
print(f"平均成功率：{analysis['avg_success_rate']:.2%}")
```

### 2. 技能质量评估 (Skill Quality)

自动评估技能库健康状况，识别低质量技能，生成优化建议。

```python
from src.skill_analyzer import SkillQualityAnalyzer

analyzer = SkillQualityAnalyzer()
report = analyzer.get_skill_library_report()
print(f"A 级技能：{report['grade_distribution']['A']}")
print(f"D 级技能：{report['grade_distribution']['D']}")
```

### 3. 智能调度引擎 (Intelligent Scheduling)

基于历史数据优化任务调度策略，支持优先级调整、资源分配、并发控制。

### 4. 进化建议生成 (Evolution Recommendations)

整合多维度数据，生成可操作的进化建议，支持效果追踪。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                   Agent Evolution                        │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   任务监控   │  │   技能分析   │  │   进化引擎   │  │
│  │  Monitoring  │  │   Analytics  │  │   Evolution  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│                  ┌────────▼────────┐                    │
│                  │  数据驱动引擎   │                    │
│                  │  Data Engine    │                    │
│                  └────────┬────────┘                    │
│                           │                             │
│         ┌─────────────────┼─────────────────┐          │
│         │                 │                 │          │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐ │
│  │ task-monitor │  │ skill-quality│  │  evolution   │ │
│  │     .db      │  │     .db      │  │  analytics   │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 📦 快速开始

### 环境要求

- Python 3.11+
- SQLite 3.42+
- 25GB+ 可用磁盘空间

### 安装

```bash
# 克隆仓库
git clone https://github.com/yadadinae/agent-evolution.git
cd agent-evolution

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 运行健康检查

```bash
# 运行系统健康检查
python src/evolve_analysis.py --health-check

# 生成进化报告
python src/evolve_analysis.py --generate-report

# 查看技能排行榜
python src/skill_analyzer.py --top-skills --limit 10
```

### 定时任务配置

```bash
# 配置 crontab (每天 03:00 执行)
0 3 * * * /path/to/agent-evolution/scripts/evolve.sh
```

---

## 📁 项目结构

```
agent-evolution/
├── src/                          # 核心源代码
│   ├── evolve_analysis.py        # 进化分析主引擎
│   ├── task_analyzer.py          # 任务性能分析
│   ├── skill_analyzer.py         # 技能质量分析
│   ├── cli_utils.py              # CLI 工具函数
│   ├── feishu_reporter.py        # 飞书通知
│   ├── wal_protocol.py           # WAL 协议
│   ├── working_buffer.py         # 工作缓冲区
│   ├── gep/                      # 遗传进化算法
│   │   ├── analyzer.js
│   │   ├── candidates.js
│   │   ├── mutation.js
│   │   └── ...
│   └── ops/                      # 运维操作
│       ├── health_check.js
│       ├── cleanup.js
│       └── ...
├── scripts/                      # 运维脚本
│   ├── evolve.sh                 # 进化执行脚本
│   ├── index.js                  # Node.js 工具
│   └── ...
├── config/                       # 配置文件
│   ├── alert-thresholds.conf     # 告警阈值
│   └── ...
├── data/                         # 数据文件
│   ├── task-monitoring.db        # 任务监控数据
│   ├── skill-quality.db          # 技能质量数据
│   └── skill-analytics.db        # 技能分析数据
├── docs/                         # 文档
│   ├── SKILL.md                  # 技能说明
│   ├── MODULE5-COMPLETE-REPORT.md
│   └── ...
├── tests/                        # 测试用例
│   ├── test_task_analyzer.py
│   ├── test_skill_analyzer.py
│   └── ...
├── assets/                       # 静态资源
│   ├── cover.png
│   └── gep/
├── examples/                     # 示例代码
│   ├── basic_usage.py
│   └── advanced_integration.py
├── requirements.txt              # Python 依赖
├── README.md                     # 本文件
└── LICENSE                       # MIT 许可证
```

---

## 🔧 核心模块

### TaskPerformanceAnalyzer

**文件**: `src/task_analyzer.py`

分析任务执行数据，识别性能瓶颈。

```python
from src.task_analyzer import TaskPerformanceAnalyzer

analyzer = TaskPerformanceAnalyzer(db_path="data/task-monitoring.db")

# 分析所有任务
analysis = analyzer.analyze_all_tasks()

# 获取健康报告
report = analyzer.get_task_health_report()

# 识别优化机会
opportunities = analyzer.identify_optimization_opportunities()
```

### SkillQualityAnalyzer

**文件**: `src/skill_analyzer.py`

评估技能库质量，生成改进建议。

```python
from src.skill_analyzer import SkillQualityAnalyzer

analyzer = SkillQualityAnalyzer(db_path="data/skill-quality.db")

# 分析技能库
analysis = analyzer.analyze_skill_library()

# 获取技能库报告
report = analyzer.get_skill_library_report()

# 识别技能缺口
gaps = analyzer.identify_skill_gaps()
```

### EvolutionEngine

**文件**: `src/evolve_analysis.py`

整合多维度数据，生成进化报告。

```python
from src.evolve_analysis import EvolutionEngine

engine = EvolutionEngine()

# 生成完整进化报告
report = engine.generate_evolution_report()

# 发送飞书通知
engine.send_feishu_notification(report)
```

---

## 💡 使用示例

### 示例 1: 基础任务分析

```python
from src.task_analyzer import TaskPerformanceAnalyzer

analyzer = TaskPerformanceAnalyzer()
analysis = analyzer.analyze_all_tasks()

print(f"总任务数：{analysis['total_tasks']}")
print(f"成功率：{analysis['avg_success_rate']:.2%}")
print(f"平均耗时：{analysis['avg_duration']:.2f}s")
print(f"健康分数：{analysis['health_score']}/100")
```

### 示例 2: 技能质量评估

```python
from src.skill_analyzer import SkillQualityAnalyzer

analyzer = SkillQualityAnalyzer()
report = analyzer.get_skill_library_report()

print("技能等级分布:")
for grade, count in report['grade_distribution'].items():
    print(f"  {grade}级：{count}个")

print("\n待优化技能:")
for skill in report['unhealthy_skills'][:5]:
    print(f"  - {skill['skill_name']} ({skill['health_score']}/100)")
```

### 示例 3: 生成进化建议

```python
from src.evolve_analysis import EvolutionEngine

engine = EvolutionEngine()
report = engine.generate_evolution_report()

print("进化建议 (按优先级排序):")
for rec in report['recommendations'][:10]:
    print(f"[{rec['priority']}] {rec['title']}")
    print(f"  预期收益：{rec['expected_benefit']}")
    print(f"  实施成本：{rec['implementation_cost']}")
```

---

## ⚙️ 配置说明

### 环境变量

```bash
# 飞书通知配置
FEISHU_APP_ID=cli_a90b5d6d8e395bc9
FEISHU_CHANNEL_ID=ou_608260b868adf690d70569214d83cfda

# 数据库路径
TASK_MONITORING_DB=data/task-monitoring.db
SKILL_QUALITY_DB=data/skill-quality.db
SKILL_ANALYTICS_DB=data/skill-analytics.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/evolution.log
```

### 告警阈值

编辑 `config/alert-thresholds.conf`:

```ini
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

---

## 🛠️ 开发指南

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_task_analyzer.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

### 代码风格

```bash
# 格式化代码
black src/ tests/

# 检查代码风格
flake8 src/ tests/

# 类型检查
mypy src/
```

### 添加新功能

1. 在 `src/` 创建新模块
2. 编写单元测试 (`tests/`)
3. 更新文档 (`docs/`)
4. 运行测试确保通过
5. 提交 Pull Request

---

## 📊 API 参考

### TaskPerformanceAnalyzer

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `analyze_all_tasks()` | 分析所有任务 | `dict` |
| `get_task_health_report()` | 获取健康报告 | `dict` |
| `identify_optimization_opportunities()` | 识别优化机会 | `list` |
| `get_recommendations()` | 获取建议列表 | `list` |

### SkillQualityAnalyzer

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `analyze_skill_library()` | 分析技能库 | `dict` |
| `get_skill_library_report()` | 获取技能库报告 | `dict` |
| `identify_skill_gaps()` | 识别技能缺口 | `list` |
| `get_recommendations()` | 获取建议列表 | `list` |

### EvolutionEngine

| 方法 | 描述 | 返回值 |
|------|------|--------|
| `generate_evolution_report()` | 生成进化报告 | `dict` |
| `send_feishu_notification()` | 发送飞书通知 | `bool` |
| `export_report_markdown()` | 导出 Markdown 报告 | `str` |
| `export_report_json()` | 导出 JSON 报告 | `str` |

---

## 📈 性能指标

基于生产环境测试数据 (2026-04-03):

| 指标 | 数值 | 目标 | 状态 |
|------|------|------|------|
| 任务分析耗时 | 16.6ms | <1s | ✅ |
| 技能分析耗时 | 9.5ms | <1s | ✅ |
| 报告生成耗时 | 18.1ms | <5s | ✅ |
| 内存占用 | <10MB | <50MB | ✅ |
| 数据库查询 | <10ms | <100ms | ✅ |
| 并发读取成功率 | 100% | >95% | ✅ |

---

## 🔍 故障排查

### 常见问题

#### 1. 数据库连接失败

```bash
# 检查数据库文件是否存在
ls -la data/*.db

# 检查数据库完整性
python -c "import sqlite3; conn = sqlite3.connect('data/task-monitoring.db'); print(conn.execute('SELECT 1').fetchone())"
```

#### 2. 飞书通知失败

```bash
# 检查环境变量
echo $FEISHU_APP_ID
echo $FEISHU_CHANNEL_ID

# 测试 API 连接
curl -X POST https://open.feishu.cn/open-apis/message/v4/send \
  -H "Authorization: Bearer $FEISHU_TOKEN" \
  -d '{"chat_id":"'$FEISHU_CHANNEL_ID'","msg_type":"text","content":{"text":"test"}}'
```

#### 3. 性能下降

```bash
# 运行性能基准测试
pytest tests/test_performance_benchmark.py -v

# 检查数据库大小
du -h data/*.db

# 清理旧数据
python scripts/cleanup.py --days 30
```

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

### 代码规范

- 遵循 PEP 8 风格指南
- 所有功能必须包含单元测试
- 代码覆盖率 >90%
- 文档完整清晰

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

## 📞 联系方式

- **作者**: 龙天涯 (@yadadinae)
- **Email**: support@studyai.ltd
- **项目地址**: https://github.com/yadadinae/agent-evolution
- **问题反馈**: https://github.com/yadadinae/agent-evolution/issues

---

## 🙏 致谢

感谢所有贡献者和使用者！

---

*Last updated: 2026-04-03*
