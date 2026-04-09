---
name: agent-evolution
description: Agent 自我进化系统。整合学习、改进、主动优化的全方位 Agent 能力提升。
version: 1.0.0
category: ai
tags: [agent, evolution, self-improvement, learning, optimization]
merged_from:
  - capability-evolver
  - self-improvement
  - proactive-agent
deprecated_skills:
  - capability-evolver
  - self-improvement
  - proactive-agent
---

# Agent Evolution - Agent 自我进化

**版本**: 2.0.0  
**合并日期**: 2026-03-08  
**整合日期**: 2026-04-01  
**状态**: ✅ 整合 proactive-agent v3.1.0 核心功能

## 概述

整合 3 个 AI 自我进化技能的统一系统，并整合 proactive-agent v3.1.0 的核心机制：
- **Capability Evolver**: 能力进化器
- **Self Improvement**: 自我改进
- **Proactive Agent**: 主动型 Agent (✅ 已整合 WAL 协议、Working Buffer、飞书主动报告)

## 新增功能 (v2.0 - 2026-04-01)

### 🆕 WAL 协议 (Write-Ahead Logging)
在进化分析前先记录关键状态，确保上下文丢失后可恢复。

**文件**: `memory/wal-protocol.md`

### 🆕 Working Buffer (工作缓冲区)
捕获危险区域（上下文使用率 >60%）的所有交换记录。

**文件**: `memory/working-buffer.md`

### 🆕 SESSION-STATE.md (会话状态)
实时记录当前任务状态，支持上下文压缩后快速恢复。

**文件**: `SESSION-STATE.md`

### 🆕 飞书主动报告机制
进化完成后自动发送飞书通知，解决"执行后无反馈"问题。

**配置**: 使用现有飞书配置 (`config.json` → `channels.feishu`)

### 🆕 上下文压缩恢复
当上下文被压缩时，从 WAL 和 Working Buffer 恢复状态。

**恢复流程**:
1. 读取 `SESSION-STATE.md` 获取当前任务状态
2. 读取 `memory/wal-protocol.md` 获取最近操作历史
3. 读取 `memory/working-buffer.md` 获取最近交换记录

## 何时使用

当用户需要：
- "改进这个技能"、"优化 Agent 能力"
- "从错误中学习"、"记录经验"
- "主动优化工作流"、"提升效率"

## 快速开始

```bash
# 分析会话历史
./evolve.sh --analyze --session current

# 识别改进点
./evolve.sh --identify-improvements

# 应用优化
./evolve.sh --apply --improvement all

# 记录学习
./evolve.sh --learn "新发现的最佳实践"

# 恢复上下文（上下文压缩后）
./evolve.sh --recover-from-compaction
```

## 核心架构

```
workspace/
├── SESSION-STATE.md       # ⭐ 活跃会话状态 (新增)
├── memory/
│   ├── wal-protocol.md    # ⭐ WAL 写前日志 (新增)
│   ├── working-buffer.md  # ⭐ 危险区域交换记录 (新增)
│   └── evolution/         # 进化报告和计划
└── skills/agent-evolution/
    ├── evolve_analysis.py # 主分析脚本
    └── src/
        ├── wal_protocol.py      # WAL 协议实现
        ├── working_buffer.py    # 工作缓冲区实现
        └── feishu_reporter.py   # 飞书报告器
```

## 核心功能

### 1. 能力进化 (Capability Evolver)

**进化流程**:

```
分析历史 → 识别改进 → 生成方案 → 应用优化 → 验证效果
```

```bash
# 分析运行时历史
./scripts/evolver.sh --analyze history

# 识别能力缺口
./scripts/evolver.sh --identify-gaps

# 生成进化方案
./scripts/evolver.sh --generate-plan

# 应用进化
./scripts/evolver.sh --apply evolution-plan.json

# 验证效果
./scripts/evolver.sh --verify
```

**进化类型**:
- 技能增强
- 工具集成
- 流程优化
- 知识更新

### 2. 自我改进 (Self Improvement)

**学习场景**:

| 场景 | 触发条件 | 操作 |
|------|----------|------|
| 命令失败 | 意外错误 | 记录错误和解决方案 |
| 用户纠正 | "不对"、"错了" | 记录正确方法 |
| 能力缺失 | "能不能..." | 创建新技能 |
| API 失败 | 外部服务错误 | 记录故障处理 |
| 知识过期 | 发现新知识 | 更新知识库 |
| 更好方法 | 发现优化方案 | 记录最佳实践 |

```bash
# 记录错误学习
./scripts/improve.sh --learn-error "命令失败原因" --solution "解决方案"

# 记录用户纠正
./scripts/improve.sh --learn-correction "原理解" --corrected "正确理解"

# 记录新知识
./scripts/improve.sh --learn-fact "新事实" --category "领域"

# 查看学习历史
./scripts/improve.sh --history

# 应用学习
./scripts/improve.sh --apply-learning
```

### 3. 主动优化 (Proactive Agent)

**主动行为**:

```bash
# 分析工作流
./scripts/proactive.sh --analyze-workflow

# 识别优化机会
./scripts/proactive.sh --identify-optimizations

# 建议改进
./scripts/proactive.sh --suggest-improvements

# 自动优化
./scripts/proactive.sh --auto-optimize

# 新能力发现
./scripts/proactive.sh --discover-capabilities
```

**优化类型**:
- 自动化重复任务
- 预取常用数据
- 优化响应时间
- 减少资源消耗

## 使用方法

### 日常进化

```bash
# 每日分析
./evolve.sh --daily-review

# 每周总结
./evolve.sh --weekly-summary

# 每月进化
./evolve.sh --monthly-evolution
```

### 学习记录

```bash
# 记录新发现
./evolve.sh --learn "发现新的 API 用法" --category "api"

# 记录错误
./evolve.sh --learn-error "API 超时" --solution "增加重试"

# 记录优化
./evolve.sh --learn-optimization "批量处理更快" --context "数据导入"
```

### 能力升级

```bash
# 检查可用升级
./evolve.sh --check-upgrades

# 安装新能力
./evolve.sh --install-capability "new-skill"

# 更新现有能力
./evolve.sh --update-capability "existing-skill"
```

## 配置指南

### 进化策略

```json
{
  "autoLearn": true,
  "autoOptimize": false,
  "reviewFrequency": "daily",
  "maxImprovements": 5,
  "verificationRequired": true
}
```

### 学习类别

```json
{
  "categories": [
    "api",
    "workflow",
    "error-handling",
    "optimization",
    "best-practices",
    "user-preferences"
  ]
}
```

## 最佳实践

### 1. 学习循环

```
执行 → 反思 → 记录 → 应用 → 验证
```

### 2. 改进优先级

| 优先级 | 类型 | 示例 |
|--------|------|------|
| P0 | 错误修复 | 崩溃、数据丢失 |
| P1 | 性能优化 | 慢查询、高延迟 |
| P2 | 用户体验 | 响应质量、准确性 |
| P3 | 代码质量 | 重构、文档 |

### 3. 知识管理

```
learnings/
├── errors/
│   └── 2026-03/
├── corrections/
│   └── 2026-03/
├── optimizations/
│   └── 2026-03/
└── capabilities/
    └── new/
```

## 向后兼容性

### 原命令仍然可用

```bash
# Capability Evolver
./capability-evolver.sh ...  # ✅

# Self Improvement
./self-improvement.sh ...    # ✅

# Proactive Agent
./proactive-agent.sh ...     # ✅
```

## 常见问题

### Q: 如何查看学习历史？

**A**: 
```bash
./evolve.sh --history
./evolve.sh --history --category error-handling
```

### Q: 进化会影响现有功能吗？

**A**: 
1. 所有进化都有验证步骤
2. 可以回滚到之前版本
3. 建议先测试环境验证

### Q: 如何禁用自动进化？

**A**: 
```bash
./evolve.sh --config autoLearn=false
```

## 废弃技能标记

- `capability-evolver` ⚠️ 已废弃
- `self-improvement` ⚠️ 已废弃
- `proactive-agent` ⚠️ 已废弃

**建议**: 新项目使用 `agent-evolution`，旧项目逐步迁移。

## 版本历史

### v1.0.0 (2026-03-08)
- ✅ 合并 3 个进化技能
- ✅ 统一学习系统
- ✅ 保留向后兼容

---

**维护者**: nanobot Team  
**许可证**: MIT
