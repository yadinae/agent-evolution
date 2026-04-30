# 🧬 Agent Evolution

> **Agent 自我进化系统** — 基于数据驱动的 AI Agent 能力提升平台

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-brightgreen.svg)]()

---

## 📖 概述

Agent Evolution 是一个完整的 AI Agent 自我进化系统，通过持续分析运行数据、识别改进机会、自动应用优化，实现 Agent 能力的持续提升。

系统采用 **4 阶段进化架构**，从基础分析到主动进化，覆盖了 Agent 能力提升的完整生命周期。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🔍 **深度分析** | 错误模式检测、工作流效率分析、API 健康检查、任务性能分析、技能质量评估 |
| 📈 **趋势追踪** | 跨周期对比、持续问题检测、恶化趋势预警、改进停滞检测 |
| 🎯 **优先级排序** | P0/P1/P2/P3 四级优先级，自动排序改进项 |
| ✅ **效果验证** | 自动验证改进是否生效，区分有效/待观察/失败 |
| 📝 **反馈循环** | 记录每个周期的改进/应用/验证数据，支持历史追溯 |
| 🔮 **主动进化** | 提前发现潜在问题，自动生成优化建议，自动创建/优化技能 |
| 📚 **知识积累** | 持续积累最佳实践、失败教训、用户偏好 |
| 🛡️ **安全机制** | WAL 协议、Working Buffer、指数退避重试 |

---

## 🏗️ 架构设计

### 4 阶段进化架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Evolution System                    │
├─────────────┬─────────────┬─────────────┬───────────────────┤
│  阶段 1     │  阶段 2      │  阶段 3      │  阶段 4            │
│  基础分析   │  增强分析    │  闭环进化    │  主动进化          │
├─────────────┼─────────────┼─────────────┼───────────────────┤
│ • 错误检测  │ • 任务性能  │ • 优先级排序 │ • 主动问题检测    │
│ • 工作流分析│ • 技能质量  │ • 效果验证   │ • 自动优化建议    │
│ • API 健康  │ • 趋势对比  │ • 反馈循环   │ • 技能进化        │
│ • 技能统计  │ • 跨周期分析│ • P0-P3 分级 │ • 知识积累        │
│ • 报告生成  │ • 自动应用  │ • 自动应用   │ • 持续学习        │
└─────────────┴─────────────┴─────────────┴───────────────────┘
```

### 模块结构

```
agent-evolution/
├── evolve_analysis.py          # 主分析器（1869 行，核心入口）
├── src/
│   ├── task_analyzer.py        # 任务性能分析器（516 行）
│   ├── skill_analyzer.py       # 技能质量分析器（467 行）
│   ├── wal_protocol.py         # WAL 写前日志协议（140 行）
│   ├── working_buffer.py       # 工作缓冲区（178 行）
│   └── feishu_reporter.py      # 飞书主动报告器（356 行）
├── scripts/
│   ├── evolve.sh               # 命令行入口脚本
│   └── index.js                # Node.js 入口
├── assets/                     # 项目资源
├── requirements.txt            # Python 依赖
└── README.md                   # 本文档
```

---

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/yadinae/agent-evolution.git
cd agent-evolution

# 安装依赖
pip install -r requirements.txt
```

### 基本用法

```bash
# 执行完整进化分析
python evolve_analysis.py --analyze

# 或使用 shell 脚本
./scripts/evolve.sh --analyze

# 指定会话
./scripts/evolve.sh --analyze --session current

# 识别改进点
./scripts/evolve.sh --identify-improvements

# 应用优化
./scripts/evolve.sh --apply --improvement all

# 记录学习
./scripts/evolve.sh --learn "新发现的最佳实践"
```

### 定时任务（Cron）

```bash
# 每天凌晨 5 点自动执行进化分析
0 5 * * * cd /path/to/agent-evolution && ./scripts/evolve.sh --analyze
```

---

## 📊 核心功能详解

### 1. 错误模式分析

自动检测 HISTORY.md 中的错误模式：

| 类别 | 检测模式 | 建议 |
|------|----------|------|
| 错误/失败 | `错误\|失败\|Error\|Failed` | 添加自动重试和降级机制 |
| HTTP 错误 | `401\|403\|404\|500\|502\|503` | 添加自动重试和降级机制 |
| 认证问题 | `API Key\|凭证\|认证` | 添加自动重试和降级机制 |
| 速率限制 | `限流\|Rate Limit\|quota` | 实现请求队列和退避策略 |

### 2. 工作流效率分析

统计高频工作流，识别自动化机会：

```
📊 备份任务: 64 次提及 → 创建专用自动化脚本
📊 网站改进: 61 次提及 → 创建专用自动化脚本
📊 技能开发: 27 次提及 → 创建专用自动化脚本
```

### 3. 任务性能分析

通过 SQLite 数据库分析任务执行数据：

- **成功率**：任务执行成功比例
- **执行时间**：平均/最小/最大耗时
- **Token 消耗**：输入/输出 Token 统计
- **错误分布**：Top 5 错误类型
- **健康评分**：综合评估任务健康度

### 4. 技能质量分析

评估技能库健康状况：

- **等级分布**：A/B/C/D 级技能数量
- **分数分布**：各维度平均分
- **问题统计**：有问题的技能数量
- **使用频率**：7 天内调用次数
- **技能缺口**：需要创建/优化的技能

### 5. 趋势对比分析

跨周期对比改进效果：

| 指标 | 上一周期 | 本周期 | 变化 |
|------|---------|--------|------|
| 改进机会 | 4 | 4 | → (+0) |
| 优化建议 | 5 | 5 | → (+0) |
| 学习记录 | 0 | 0 | → (+0) |

### 6. 优先级排序

自动为改进项分配优先级：

| 优先级 | 条件 | 示例 |
|--------|------|------|
| **P0** | 阻塞性问题（成功率<80%、安全漏洞） | 高严重性错误处理 |
| **P1** | 重要问题（API 可靠性、工作流优化） | API 降级方案 |
| **P2** | 一般问题（技能文档补充） | 文档完善 |
| **P3** | 低优先级改进 | 体验优化 |

### 7. 改进效果验证

自动验证上次周期的改进是否生效：

| 状态 | 说明 | 操作 |
|------|------|------|
| ✅ **有效** | 改进已生效 | 记录为成功模式 |
| ⏳ **待观察** | 部分生效或需持续监控 | 下周期继续验证 |
| ❌ **失败** | 改进未生效 | 重新评估策略 |

### 8. 主动问题检测

提前发现潜在问题：

- **持续问题**：连续 2+ 周期出现的问题
- **恶化趋势**：问题数量增长 >50%
- **新出现模式**：内存/超时/配额等新问题
- **改进停滞**：3 周期未应用任何改进

### 9. 技能进化

自动创建/优化技能：

```
🧬 技能进化...
  - create: backup-automation（高频工作流：备份任务）
  - create: website-optimization（高频工作流：网站改进）
```

### 10. 知识积累

持续积累最佳实践和教训：

| 类型 | 说明 | 上限 |
|------|------|------|
| 有效模式 | 已验证有效的改进模式 | 50 条 |
| 失败教训 | 改进失败的原因和策略 | 50 条 |
| 用户偏好 | 用户明确表达的偏好 | 50 条 |
| 最佳实践 | 高优先级优化建议 | 50 条 |

---

## 📁 输出文件

进化分析完成后，生成以下文件：

| 文件 | 说明 |
|------|------|
| `evolution-report-YYYY-MM-DD.md` | 进化报告（含趋势对比、验证结果） |
| `evolution-plan-YYYY-MM-DD.json` | 进化计划（含改进项、优先级） |
| `feedback-log.json` | 反馈循环记录（历史周期数据） |
| `knowledge-base.json` | 知识库（最佳实践/教训/偏好） |
| `wal-protocol.md` | WAL 写前日志（状态恢复） |
| `working-buffer.md` | 工作缓冲区（危险区域记录） |
| `SESSION-STATE.md` | 会话状态（当前任务状态） |

---

## 🔧 配置说明

### 环境变量

```bash
# .env 文件
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
WORKSPACE=/home/admin/.nanobot/workspace
```

### 数据库路径

```python
# 任务监控数据库
task_monitoring_db = "/home/admin/.nanobot/workspace/task-monitoring.db"

# 技能质量数据库
quality_db = "/home/admin/.nanobot/workspace/skill-quality.db"

# 技能分析数据库
analytics_db = "/home/admin/.nanobot/workspace/skills/skill-analytics/skill-analytics.db"
```

---

## 📈 进化效果

### 阶段 1 → 阶段 4 演进

| 阶段 | 核心能力 | 完成日期 |
|------|----------|----------|
| 阶段 1 | 基础分析（错误检测、工作流分析、API 健康） | 2026-04-24 |
| 阶段 2 | 增强分析（任务性能、技能质量、趋势对比） | 2026-04-30 |
| 阶段 3 | 闭环进化（优先级排序、效果验证、反馈循环） | 2026-04-30 |
| 阶段 4 | 主动进化（主动检测、自动建议、技能进化、知识积累） | 2026-04-30 |

### 关键指标

- **错误检测**：113 次错误事件 → 自动分类和建议
- **工作流优化**：64 次备份任务 → 自动创建专用技能
- **技能覆盖**：30+ 技能 → 自动扫描和评估
- **趋势追踪**：多周期对比 → 持续问题检测

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- **WAL 协议**：受数据库 Write-Ahead Logging 启发
- **技能分析**：基于 Hermes Agent 技能系统
- **飞书集成**：使用飞书开放平台 API

---

## 📮 联系方式

- **GitHub**: [yadinae](https://github.com/yadinae)
- **仓库**: [agent-evolution](https://github.com/yadinae/agent-evolution)

---

<div align="center">

**🧬 Agent Evolution — 让 AI Agent 持续进化**

*Built with ❤️ by yadinae*

</div>
