# GitHub 仓库配置指南 📝

本指南说明如何配置 GitHub 仓库的 About、Topics、分支保护等设置。

---

## 仓库 About 描述

### 建议的 About 内容

```
🧬 Agent 自我进化系统 - 基于数据驱动的 AI Agent 能力提升平台

✨ 核心功能：
• 任务性能监控与分析
• 技能质量评估与优化
• 智能调度引擎
• 自动化进化建议
• 实时健康评分系统

📊 生产验证：95%+ 测试覆盖率，<20ms 分析延迟，75%+ 自动实施率

📚 完整文档：docs/AGENT-EVOLUTION-FOUR-LAYERS-ARCHITECTURE.md
```

### 设置方法

#### 方法 1: GitHub 网页手动设置

1. 访问仓库：https://github.com/yadinae/agent-evolution
2. 点击右上角 ⚙️ 图标 (Settings)
3. 在 "About" 区域点击齿轮图标
4. 粘贴上述描述
5. 点击 "Save changes"

#### 方法 2: 使用 GitHub CLI

```bash
# 安装 GitHub CLI (如果未安装)
# Ubuntu/Debian:
sudo apt install gh

# macOS:
brew install gh

# 登录 GitHub
gh auth login

# 更新仓库描述
gh repo edit yadinae/agent-evolution \
  --description "🧬 Agent 自我进化系统 - 基于数据驱动的 AI Agent 能力提升平台 | ✨ 任务监控/技能评估/智能调度/自动进化 | 📊 95%+ 测试覆盖，<20ms 延迟"
```

---

## Topics 标签

### 建议的 Topics

```
ai-agent
self-improvement
machine-learning
automation
performance-monitoring
skill-evaluation
intelligent-scheduling
data-driven
python
open-source
agent-evolution
ai-optimization
```

### 设置方法

#### GitHub 网页

1. 访问仓库主页
2. 在 About 区域右侧点击 "Add topics"
3. 逐个添加上述标签
4. 按 Enter 确认每个标签

#### GitHub CLI

```bash
gh repo edit yadinae/agent-evolution \
  --add-topic ai-agent \
  --add-topic self-improvement \
  --add-topic machine-learning \
  --add-topic automation \
  --add-topic performance-monitoring \
  --add-topic skill-evaluation \
  --add-topic intelligent-scheduling \
  --add-topic data-driven \
  --add-topic python \
  --add-topic open-source \
  --add-topic agent-evolution \
  --add-topic ai-optimization
```

---

## 分支保护规则

### 建议的分支保护

#### main 分支保护

1. **Require a pull request before merging**
   - ✅ Require approvals: 1
   - ✅ Dismiss stale pull request approvals when new commits are pushed

2. **Require status checks to pass before merging**
   - ✅ Require branches to be up to date before merging
   - 选择必需的状态检查:
     - ✅ CI / test (Python 3.9)
     - ✅ CI / test (Python 3.10)
     - ✅ CI / test (Python 3.11)
     - ✅ CI / lint

3. **Require conversation resolution before merging**
   - ✅ All conversations must be resolved

4. **Include administrators**
   - ✅ Apply to administrators (可选)

#### 设置方法

**GitHub 网页**:
1. Settings → Branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. 勾选上述选项
5. Click "Create"

**GitHub CLI**:
```bash
# 注意：分支保护需要通过 GitHub API 设置
# 使用以下 curl 命令：

curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/yadinae/agent-evolution/branches/main/protection \
  -d '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["CI / test (Python 3.9)", "CI / test (Python 3.10)", "CI / test (Python 3.11)", "CI / lint"]
    },
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": true
    },
    "restrictions": null,
    "enforce_admins": false
  }'
```

---

## GitHub Actions 配置

### 启用 GitHub Actions

1. 访问 https://github.com/yadinae/agent-evolution/actions
2. 如果是首次访问，点击 "I understand my workflows, go ahead and enable them"
3. 确认以下工作流已启用：
   - ✅ CI/CD Pipeline
   - ✅ Release Drafter

### 配置 Secrets

#### 必需 Secrets

1. **CODECOV_TOKEN** (可选，用于代码覆盖率)
   - 访问 https://codecov.io/
   - 添加仓库
   - 获取 Upload Token
   - Settings → Secrets and variables → Actions → New repository secret
   - Name: `CODECOV_TOKEN`
   - Value: `<your-token>`

2. **PYPI_API_TOKEN** (可选，用于自动发布到 PyPI)
   - 访问 https://pypi.org/manage/account/token/
   - 创建 API token
   - Settings → Secrets and variables → Actions → New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: `pypi-<your-token>`

3. **FEISHU_APP_ID** (用于飞书通知)
   - Name: `FEISHU_APP_ID`
   - Value: `cli_a90b5d6d8e395bc9`

4. **FEISHU_CHANNEL_ID** (用于飞书通知)
   - Name: `FEISHU_CHANNEL_ID`
   - Value: `ou_608260b868adf690d70569214d83cfda`

---

## 徽章配置

### README 徽章

在 README.md 中添加以下徽章：

```markdown
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yadinae/agent-evolution/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/yadinae/agent-evolution/actions)
[![Coverage](https://codecov.io/gh/yadinae/agent-evolution/branch/main/graph/badge.svg)](https://codecov.io/gh/yadinae/agent-evolution)
[![Issues](https://img.shields.io/github/issues/yadinae/agent-evolution.svg)](https://github.com/yadinae/agent-evolution/issues)
[![Stars](https://img.shields.io/github/stars/yadinae/agent-evolution.svg)](https://github.com/yadinae/agent-evolution/stargazers)
[![Forks](https://img.shields.io/github/forks/yadinae/agent-evolution.svg)](https://github.com/yadinae/agent-evolution/network)
```

### 徽章说明

| 徽章 | 说明 | 来源 |
|------|------|------|
| Python Version | Python 版本要求 | shields.io |
| License | 许可证类型 | shields.io |
| CI/CD Status | CI/CD 状态 | GitHub Actions |
| Coverage | 代码覆盖率 | Codecov |
| Issues | 问题数量 | shields.io |
| Stars | 星标数量 | shields.io |
| Forks | 派生数量 | shields.io |

---

## 发布管理

### 使用 Release Drafter

Release Drafter 会自动根据 PR 和标签创建 Release Notes 草稿。

#### 配置步骤

1. 确保 `.github/release-drafter.yml` 已存在
2. 确保 `.github/workflows/release-drafter.yml` 已启用
3. 创建 PR 时使用以下标签：
   - `breaking` - 破坏性变更
   - `feature` - 新功能
   - `enhancement` - 功能增强
   - `bug` - Bug 修复
   - `documentation` - 文档更新
   - `internal` - 内部改进

#### 创建发布

1. 访问 https://github.com/yadinae/agent-evolution/releases
2. 点击 "Draft a new release"
3. 选择标签或创建新标签 (如 `v1.0.0`)
4. Release Drafter 会自动填充发布说明
5. 点击 "Publish release"

---

## 问题模板

### 创建 Issue 模板

在 `.github/ISSUE_TEMPLATE/` 目录下创建模板：

#### Bug 报告模板

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: 报告一个 Bug
title: "[Bug]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        感谢报告 Bug！请提供以下信息帮助我们复现问题。
  - type: textarea
    id: description
    attributes:
      label: Bug 描述
      description: 清晰简洁地描述 Bug
    validations:
      required: true
  - type: textarea
    id: reproduction
    attributes:
      label: 复现步骤
      description: 复现 Bug 的步骤
      placeholder: |
        1. 执行 '...'
        2. 看到错误
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: 期望行为
      description: 期望发生什么
    validations:
      required: true
  - type: textarea
    id: actual
    attributes:
      label: 实际行为
      description: 实际发生了什么
    validations:
      required: true
  - type: input
    id: environment
    attributes:
      label: 环境信息
      placeholder: Python 版本、操作系统等
  - type: textarea
    id: logs
    attributes:
      label: 日志输出
      description: 粘贴相关日志
      render: shell
```

#### 功能请求模板

```yaml
# .github/ISSUE_TEMPLATE/feature_request.yml
name: Feature Request
description: 建议一个新功能
title: "[Feature]: "
labels: ["enhancement"]
body:
  - type: markdown
    attributes:
      value: |
        感谢提出功能建议！请提供以下信息。
  - type: textarea
    id: problem
    attributes:
      label: 相关问题
      description: 这个功能解决了什么问题？
    validations:
      required: true
  - type: textarea
    id: solution
    attributes:
      label: 建议的解决方案
      description: 你希望如何实现这个功能？
    validations:
      required: true
  - type: textarea
    id: alternatives
    attributes:
      label: 其他方案
      description: 你还考虑过哪些替代方案？
  - type: textarea
    id: context
    attributes:
      label: 补充信息
      description: 任何其他背景或截图
```

---

## Pull Request 模板

### 创建 PR 模板

```markdown
# .github/pull_request_template.md

## 📋 变更类型

<!-- 选择适用的类型，删除不适用的 -->

- [ ] Bug 修复 (非破坏性变更，修复 Issue)
- [ ] 新功能 (非破坏性变更，添加功能)
- [ ] 破坏性变更 (修复或功能会破坏现有行为)
- [ ] 文档更新
- [ ] 代码重构 (无功能变更)
- [ ] 性能优化
- [ ] 测试添加

## 📝 描述

<!-- 清晰简洁地描述此 PR 做了什么 -->

## 🔗 关联 Issue

<!-- 如果适用，使用 "Fixes #123" 或 "Closes #123" 语法 -->

Fixes #

## 🧪 测试

<!-- 描述你运行的测试 -->

- [ ] 已添加单元测试
- [ ] 已运行所有测试并通过
- [ ] 已手动测试

## ✅ 检查清单

- [ ] 我的代码遵循项目的代码规范
- [ ] 我已对代码进行自我审查
- [ ] 我已添加/更新文档
- [ ] 我的更改没有引入新的警告
- [ ] 我已在本地测试过这些更改

## 📸 截图 (如果适用)

<!-- 如果 UI 有变更，添加截图 -->

## 📋 发布说明

<!-- 这些更改将如何在发布说明中呈现？ -->
```

---

## 贡献者指南

### 创建 CONTRIBUTING.md

```markdown
# 贡献指南

欢迎贡献！请遵循以下步骤：

## 开发环境设置

1. Fork 仓库
2. 克隆你的 Fork
3. 创建虚拟环境
4. 安装依赖
5. 创建功能分支

## 提交流程

1. 创建功能分支 (`git checkout -b feature/amazing-feature`)
2. 进行更改
3. 运行测试 (`pytest tests/ -v`)
4. 提交更改 (`git commit -m 'Add amazing feature'`)
5. 推送到分支 (`git push origin feature/amazing-feature`)
6. 创建 Pull Request

## 代码规范

- 遵循 PEP 8
- 使用 Black 格式化代码
- 添加类型注解
- 编写单元测试
- 更新文档

## 测试要求

- 所有新功能必须包含测试
- 代码覆盖率 >90%
- 所有测试必须通过

## 发布流程

- 使用语义化版本 (SemVer)
- 更新 CHANGELOG.md
- 创建 Git 标签
- 发布到 PyPI (如果适用)

感谢你的贡献！
```

---

## 安全检查清单

在合并 PR 前，请确认：

- [ ] 代码通过所有 CI 检查
- [ ] 代码覆盖率未下降
- [ ] 无安全漏洞
- [ ] 依赖项已更新
- [ ] 文档已更新
- [ ] 变更已测试

---

## 维护者指南

### 日常维护

1. **审查 PR**
   - 检查代码质量
   - 确认测试通过
   - 验证文档更新

2. **管理 Issue**
   - 标记和分类
   - 分配负责人
   - 设置优先级

3. **发布管理**
   - 定期发布新版本
   - 更新发布说明
   - 通知用户

4. **社区管理**
   - 回答问题和反馈
   - 鼓励贡献
   - 维护行为准则

---

*文档版本：1.0.0*  
*创建时间：2026-04-03*  
*最后更新：2026-04-03*
