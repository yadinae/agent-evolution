# ⚠️ GitHub Actions 工作流配置说明

## ✅ 代码已推送成功

**仓库地址**: https://github.com/yadinae/agent-evolution

**当前状态**: 
- ✅ 所有源代码已推送 (72 个文件)
- ✅ 文档已推送
- ✅ 测试已推送
- ⚠️ GitHub Actions 工作流暂未推送（需要 workflow 权限）

---

## 🔧 为什么工作流未推送？

当前使用的 GitHub Token **缺少 `workflow` 权限**。

GitHub 安全策略要求：
- 创建或更新 `.github/workflows/` 目录下的文件
- 需要 Personal Access Token 具有 `workflow` scope
- 当前 Token 只有 `repo` 权限

⚠️ **注意**: 请勿在文档中硬编码 Token！应使用环境变量或 GitHub Secrets。

---

## 📋 解决方案（3 选 1）

### 方案 1: 更新 Token 权限（推荐）⭐

1. **访问 Token 设置**
   https://github.com/settings/tokens

2. **找到当前 Token**
   - 名称：可能是 `nanobot-backup` 或类似
   - 最后几位：`EZWv`

3. **更新权限**
   - 点击 "Update" 或 "Regenerate"
   - 勾选额外权限：
     - ✅ `workflow` (Update GitHub Action workflows)
   - 保存并复制新 Token

4. **更新本地配置**
   ```bash
   # 编辑 .env 文件（不要提交到 Git！）
   nano /home/admin/.nanobot/workspace/.env
   
   # 更新为新的 Token（确保包含 workflow 权限）
   GITHUB_TOKEN=<你的新令牌>
   ```

5. **重新推送工作流**
   ```bash
   cd /home/admin/.nanobot/workspace/github-repos/agent-evolution
   git remote set-url origin "https://<TOKEN>@github.com/yadinae/agent-evolution.git"
   git push
   ```

---

### 方案 2: 在 GitHub 网页手动创建工作流

1. **访问仓库**
   https://github.com/yadinae/agent-evolution

2. **点击 "Add file" → "Create new file"**

3. **创建第一个工作流**
   - 文件名：`.github/workflows/ci-cd.yml`
   - 内容：复制本地文件内容
   ```bash
   cat .github/workflows/ci-cd.yml
   ```

4. **提交更改**
   - Commit message: `ci: Add CI/CD workflow`
   - 点击 "Commit new file"

5. **重复步骤 2-4 创建第二个工作流**
   - 文件名：`.github/workflows/release-drafter.yml`
   - 内容：
   ```bash
   cat .github/workflows/release-drafter.yml
   ```

---

### 方案 3: 使用 GitHub CLI 推送工作流

```bash
# 使用 gh CLI（已有认证）
cd /home/admin/.nanobot/workspace/github-repos/agent-evolution

# 恢复工作流目录
git mv .github/workflows-disabled .github/workflows
git add .github
git commit -m "ci: Add GitHub Actions workflows"

# 使用 gh CLI 推送（不受 Token 限制）
gh api repos/yadinae/agent-evolution/contents/.github/workflows/ci-cd.yml \
  --method PUT \
  -f message="ci: Add CI/CD workflow" \
  -f content="$(base64 .github/workflows/ci-cd.yml)" \
  -f branch=main

gh api repos/yadinae/agent-evolution/contents/.github/workflows/release-drafter.yml \
  --method PUT \
  -f message="ci: Add Release Drafter workflow" \
  -f content="$(base64 .github/workflows/release-drafter.yml)" \
  -f branch=main
```

---

## 📄 工作流文件内容

### ci-cd.yml

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v --tb=short
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install flake8
      run: pip install flake8
    
    - name: Lint with flake8
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

  build:
    runs-on: ubuntu-latest
    needs: [test, lint]
    steps:
    - uses: actions/checkout@v4
    
    - name: Build package
      run: |
        python -m pip install --upgrade build
        python -m build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist
        path: dist/
```

### release-drafter.yml

```yaml
name: Release Drafter

on:
  push:
    branches:
      - main
  pull_request:
    types: [opened, reopened, synchronize]

permissions:
  contents: read

jobs:
  update_release_draft:
    permissions:
      contents: write
      pull-requests: write
    runs-on: ubuntu-latest
    steps:
      - uses: release-drafter/release-drafter@v5
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## ✅ 验证工作流

推送或创建工作流后，访问：
https://github.com/yadinae/agent-evolution/actions

应该能看到：
- ✅ CI/CD Pipeline 工作流
- ✅ Release Drafter 工作流
- ✅ 自动触发首次运行

---

## 🎯 当前仓库状态

**已推送内容**:
```
✅ 72 个文件
✅ 13,450+ 行代码
✅ README.md (带徽章)
✅ 完整文档
✅ 测试套件
✅ 示例代码
✅ 配置脚本
✅ CI/CD 工作流配置（本地）
⏳ GitHub Actions 工作流（待手动添加或更新 Token 后推送）
```

**访问仓库**:
https://github.com/yadinae/agent-evolution

---

## 📞 快速操作命令

```bash
# 查看当前提交
cd /home/admin/.nanobot/workspace/github-repos/agent-evolution
git log --oneline

# 查看远程状态
git remote -v

# 查看未推送的提交
git status

# 查看工作流文件
cat .github/workflows-disabled/ci-cd.yml
cat .github/workflows-disabled/release-drafter.yml
```

---

**创建时间**: 2026-04-03 05:45 UTC  
**最后更新**: 2026-04-03 05:45 UTC  
**状态**: ⏳ 等待工作流配置
