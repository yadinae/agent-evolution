# Hermes Ralph Loop — Level 2 文档

## 设计理念

**层次 1（Phase 1）**: Cron 包装器检查完成标准
**层次 2（任务级 Ralph Loop）**: 解析任务输出 → 提取结构化状态 → 生成可操作的反馈

层次 2 的核心：任务本身输出**可被下次循环消费的结构化上下文**。

```
不是简单重试（从头开始）
而是基于上次成果改进（知道做了什么、还需要做什么）
```

## Level 2 架构

```
┌───────────────────────────────────────────────┐
│            3:00 AM — 原始 Cron 任务            │
│  ┌─────────────────────────────────────────┐  │
│  │ 1. 启动时检查 Ralph Loop 状态文件        │  │
│  │ 2. 如果存在 → 读取结构化反馈：          │  │
│  │    - actions_completed（已完成操作）     │  │
│  │    - remaining_issues（待解决问题）      │  │
│  │    - next_action_hint（下一步建议）      │  │
│  │ 3. 基于反馈继续优化（不重复已完成操作）  │  │
│  │ 4. 输出日报                              │  │
│  └─────────────────────────────────────────┘  │
└───────────────────┬───────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────┐
│        3:35 AM — Ralph Loop Level 2 验证器     │
│  ┌─────────────────────────────────────────┐  │
│  │ python3 ralph-wrapper.py analyze <job>  │  │
│  │                                         │  │
│  │ 1. 解析 cron 输出（TaskOutputParser）    │  │
│  │    - 提取指标、操作、问题、待办          │  │
│  │ 2. 验证完成标准                          │  │
│  │ 3. 生成反馈（FeedbackGenerator）         │  │
│  │    - 成功：清除状态文件                  │  │
│  │    - 失败：保存结构化状态到状态文件      │  │
│  │ 4. 状态文件包含：                       │  │
│  │    - iteration/max_iterations            │  │
│  │    - completion: passed/reason           │  │
│  │    - actions_completed                   │  │
│  │    - remaining_issues                    │  │
│  │    - next_action_hint                    │  │
│  │    - human_readable（人类可读反馈）      │  │
│  └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

## 文件结构

```
~/.hermes/
├── cron/
│   ├── ralph-config.json           # Ralph Loop 配置
│   ├── ralph-state/                # 运行时状态文件
│   │   └── 1e3dc07baae4.json       # 结构化状态（Level 2 格式）
│   └── output/
│       └── 1e3dc07baae4/           # cron 任务输出
│           └── 2026-05-02_03-16-10.md
└── bin/
    └── ralph-wrapper.py            # Level 2 工具脚本

~/projects/agent-evolution/v2/
├── ralph-output-template.json      # 任务输出模板示例
└── RALPH-LOOP.md                   # 完整文档
```

## Level 2 状态文件格式

```json
{
  "iteration": 2,
  "max_iterations": 3,
  "timestamp": "2026-05-03 03:36",
  "job_id": "1e3dc07baae4",
  "output_file": "2026-05-03_03-16-10.md",
  "completion": {
    "passed": false,
    "details": {
      "reason": "新增提示词只有 3 个，目标 ≥5"
    }
  },
  "actions_completed": [
    "✅ 修复了 244 个通用标签",
    "✅ 统一了 AI绘画/AI 绘画 标签格式"
  ],
  "remaining_issues": [
    "creative 分类只有 19 个，目标 25 个",
    "investment 分类只有 21 个，目标 25 个"
  ],
  "should_continue": true,
  "next_action_hint": "重点补充 creative 和 investment 分类的提示词，每个分类至少新增 4 个高质量提示词",
  "human_readable": "🔄 Ralph Loop - 第 2 次迭代\n\n上次已完成的操作：\n  ✅ 修复了 244 个通用标签\n  ✅ 统一了 AI绘画/AI 绘画 标签格式\n\n未达标原因：新增提示词只有 3 个，目标 ≥5\n\n待解决的问题：\n  - creative 分类只有 19 个，目标 25 个\n  - investment 分类只有 21 个，目标 25 个\n\n请继续优化，重点关注以上未解决的问题。"
}
```

## Level 2 vs Level 1 对比

| 维度 | Level 1 | Level 2 |
|------|---------|---------|
| **状态存储** | 手动创建 | 自动解析生成结构化数据 |
| **反馈内容** | 简单模板填充 | 包含已完成操作、待办、下一步建议 |
| **任务感知** | 不知道任务做了什么 | 知道具体完成了哪些动作、卡在哪里 |
| **分析能力** | 只检查 shell 命令返回值 | 解析完整输出，提取指标/操作/问题 |
| **反馈格式** | 纯文本 | JSON 结构化 + human_readable 文本 |

## 命令行工具

```bash
# 查看状态
python3 ~/.hermes/bin/ralph-wrapper.py status

# 分析最近一次运行，生成结构化反馈
python3 ~/.hermes/bin/ralph-wrapper.py analyze 1e3dc07baae4

# 检查是否达标
python3 ~/.hermes/bin/ralph-wrapper.py check 1e3dc07baae4
```

## 当前配置的任务

| 任务 | 启用 | 最大迭代 | 完成标准 |
|------|------|---------|---------|
| StudyAI 优化 | ✅ 是 | 3 | 提示词总数 ≥ 1403 |
| Redis 备份验证 | ❌ 否 | 2 | 备份文件存在 |

## 工作原理

### 正常运行流程

1. **3:00 AM**: StudyAI 优化任务启动
   - 检查 `~/.hermes/cron/ralph-state/1e3dc07baae4.json`
   - 如果存在 → 读取 `next_action_hint` 和 `remaining_issues`
   - 基于反馈继续优化，不重复已完成操作
   - 输出日报

2. **3:35 AM**: Ralph Loop Level 2 验证器启动
   - 执行 `python3 ralph-wrapper.py analyze 1e3dc07baae4`
   - 解析输出：提取指标、操作、问题、待办
   - 检查完成标准
   - 达标 → 清除状态文件
   - 未达标 → 保存结构化状态（含反馈）

3. **第二天 3:00 AM**: 优化任务再次启动
   - 检测到状态文件存在
   - 读取结构化反馈
   - 看到上次做了什么、还需要做什么
   - 基于具体建议继续优化

### 安全网

- **最大迭代次数**: 默认 3 次
- **状态自动清除**: 达标或达上限后自动清除
- **不修改原始任务代码**: 通过状态文件注入上下文
- **基线值保护**: `/tmp/studyai_baseline.json`

## Level 2 核心模块

### TaskOutputParser

解析 cron 输出文件，提取：
- 关键指标（提示词总数、新增数量等）
- 已完成操作（✅ 开头的行）
- 发现的问题（[严重]、[中等]、[轻微]、⚠️）
- 待办事项（- [ ] 格式）
- 下一步建议

### FeedbackGenerator

基于解析结果生成反馈：
- 检查完成标准
- 计算迭代次数
- 生成成功/继续迭代反馈
- 提供人类可读摘要

### RalphStateManager

状态文件管理：
- 加载/保存/清除状态
- 保持结构化 JSON 格式
- 支持历史迭代记录

## Phase 2 规划

- 支持更多任务类型（Redis 备份验证、新闻简报等）
- 自动更新基线值
- 支持多任务同时循环
- 状态文件历史追踪
