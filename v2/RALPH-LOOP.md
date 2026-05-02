# Hermes Ralph Loop — Phase 1 文档

## 设计理念

Ralph Loop 的核心理念（来自 Anthropic 官方插件）：**让 AI 在循环中看到自己上次的工作成果，持续改进直到达标。**

```
不是简单重试（从头开始）
而是 Ralph Loop（基于上次成果改进）
```

## Phase 1 架构

```
┌───────────────────────────────────────────────┐
│            3:00 AM — 原始 Cron 任务            │
│  ┌─────────────────────────────────────────┐  │
│  │ 1. 启动时检查 Ralph Loop 状态文件        │  │
│  │ 2. 如果存在 → 读取反馈上下文            │  │
│  │ 3. 执行优化/改进工作                    │  │
│  │ 4. 输出日报                              │  │
│  └─────────────────────────────────────────┘  │
└───────────────────┬───────────────────────────┘
                    │
                    ▼
┌───────────────────────────────────────────────┐
│        3:35 AM — Ralph Loop 验证器             │
│  ┌─────────────────────────────────────────┐  │
│  │ 1. 读取日报输出                          │  │
│  │ 2. 检查完成标准（API/文件/指标）          │  │
│  │ 3. 达标 → 清除状态文件，结束循环         │  │
│  │ 4. 未达标 → 保存状态+反馈到状态文件      │  │
│  │    → 下次 3AM 任务启动时自动注入         │  │
│  │ 5. 达最大迭代 → 清除，标记最终结果       │  │
│  └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

## 文件结构

```
~/.hermes/
├── cron/
│   ├── ralph-config.json        # Ralph Loop 配置（完成标准、迭代上限）
│   ├── ralph-state/             # 运行时状态文件
│   │   └── 1e3dc07baae4.json    # 特定 job 的当前循环状态
│   └── output/
│       └── 1e3dc07baae4/        # cron 任务输出
│           └── 2026-05-02_03-16-10.md
└── bin/
    └── ralph-wrapper.py         # Ralph Loop 工具脚本
```

## 配置格式

`~/.hermes/cron/ralph-config.json`:

```json
{
  "jobs": {
    "<job_id>": {
      "name": "任务名称",
      "enabled": true,
      "max_iterations": 3,
      "completion_criteria": {
        "type": "shell",
        "check": "python3 -c \"验证脚本\"",
        "description": "人类可读的描述",
        "timeout_seconds": 15
      },
      "feedback_template": "反馈模板"
    }
  }
}
```

## 状态文件格式

`~/.hermes/cron/ralph-state/<job_id>.json`:

```json
{
  "iteration": 2,
  "max_iterations": 3,
  "last_check": "2026-05-03 03:36",
  "last_result": "未通过: 新增提示词只有 3 个，目标 ≥5",
  "should_continue": true,
  "feedback": "【Ralph Loop - 第 2 次迭代】\n\n上次已完成：\n- 修复了 10 个分类错误\n\n未达标原因：\n新增提示词只有 3 个，目标 ≥5\n\n请继续优化，重点关注未解决的问题。"
}
```

## 命令行工具

```bash
# 查看状态
python3 ~/.hermes/bin/ralph-wrapper.py status

# 检查指定 job
python3 ~/.hermes/bin/ralph-wrapper.py check 1e3dc07baae4

# 手动触发循环
python3 ~/.hermes/bin/ralph-wrapper.py run 1e3dc07baae4
```

## 当前配置的任务

| 任务 | 启用 | 最大迭代 | 完成标准 |
|------|------|---------|---------|
| StudyAI 优化 | ✅ 是 | 3 | 提示词总数 ≥ 基线值 |
| Redis 备份验证 | ❌ 否 | 2 | 备份文件存在 |

## 工作原理

1. **3:00 AM**: StudyAI 优化任务启动
   - 启动时检查 `~/.hermes/cron/ralph-state/1e3dc07baae4.json`
   - 如果存在 → 读取 feedback，继续改进
   - 如果不存在 → 正常执行

2. **3:35 AM**: Ralph Loop 验证器启动
   - 读取优化日报
   - 检查 `curl -s 'https://www.studyai.ltd/api/prompts?pageSize=1' | jq '.total'` ≥ 基线值
   - 达标 → 清除状态文件
   - 未达标 → 保存状态文件（含反馈）

3. **第二天 3:00 AM**: 优化任务再次启动
   - 检测到状态文件存在
   - 读取反馈上下文
   - 基于上次成果继续优化
   - ...

## 安全网

- **最大迭代次数**: 默认 3 次，防止无限循环
- **状态自动清除**: 达标或达上限后自动清除
- **不修改原始任务代码**: 通过状态文件注入上下文，无需改代码
- **基线值保护**: 基线值单独存储在 `/tmp/studyai_baseline.json`

## Phase 2 规划

- 支持更多类型的完成标准（API 返回、日志关键字、文件变更）
- 自动修改 cron job prompt 中的反馈上下文
- 支持多个任务同时循环
