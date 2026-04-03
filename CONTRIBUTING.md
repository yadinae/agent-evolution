# 贡献指南

感谢你对 Agent Evolution 项目的关注！我们欢迎各种形式的贡献。

## 📋 目录

- [行为准则](#-行为准则)
- [我能贡献什么](#-我能贡献什么)
- [开发环境设置](#-开发环境设置)
- [提交流程](#-提交流程)
- [代码规范](#-代码规范)
- [测试要求](#-测试要求)
- [文档规范](#-文档规范)
- [发布流程](#-发布流程)

---

## 🤝 行为准则

本项目采用 [贡献者公约](https://www.contributor-covenant.org/) 行为准则。请确保：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

---

## 💡 我能贡献什么

### 1. 报告 Bug

发现 Bug？请创建 Issue 并包含：

- 清晰的标题和描述
- 复现步骤
- 预期行为和实际行为
- 环境信息（Python 版本、操作系统等）
- 相关日志和截图

### 2. 提出新功能

有新想法？请创建 Issue 并说明：

- 功能描述和使用场景
- 为什么这个功能很重要
- 可能的实现方案
- 潜在的兼容性影响

### 3. 提交代码

可以直接提交 Pull Request：

- 修复 Typo 或文档错误
- 改进现有功能
- 添加新特性
- 优化性能
- 增加测试覆盖率

### 4. 改进文档

文档同样重要：

- 修正文档错误
- 补充缺失的说明
- 添加示例代码
- 翻译文档

---

## 🛠️ 开发环境设置

### 1. Fork 和克隆

```bash
# Fork 项目
# 在 GitHub 上点击 Fork 按钮

# 克隆到本地
git clone https://github.com/YOUR_USERNAME/agent-evolution.git
cd agent-evolution

# 添加上游仓库
git remote add upstream https://github.com/yadadinae/agent-evolution.git
```

### 2. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### 3. 创建分支

```bash
# 从 develop 分支创建新分支
git checkout develop
git checkout -b feature/your-feature-name

# 或者修复 Bug
git checkout -b fix/bug-fix-name
```

---

## 📝 提交流程

### 1. 开发流程

```bash
# 保持分支同步
git fetch upstream
git rebase upstream/develop

# 开发功能
# ... 编写代码和测试 ...

# 运行测试
pytest tests/ -v

# 格式化代码
black src/ tests/

# 检查代码风格
flake8 src/ tests/

# 提交更改
git add .
git commit -m "feat: add new feature"

# 推送到远程
git push origin feature/your-feature-name
```

### 2. 创建 Pull Request

1. 在 GitHub 上访问你的 Fork
2. 点击 "Compare & pull request"
3. 填写 PR 描述（使用模板）
4. 等待 CI 检查通过
5. 等待代码审查

### 3. PR 模板

```markdown
## 描述
简要描述此 PR 的目的

## 相关 Issue
Fixes #123

## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 文档更新
- [ ] 性能优化
- [ ] 重构
- [ ] 测试

## 测试
- [ ] 已添加单元测试
- [ ] 所有测试通过
- [ ] 已手动测试

## 截图（如适用）
添加相关截图
```

---

## 📏 代码规范

### Python 代码风格

遵循 [PEP 8](https://pep8.org/) 规范：

```python
# ✅ 好的代码
def calculate_health_score(tasks, skills):
    """计算健康分数"""
    if not tasks or not skills:
        return 0
    
    task_score = sum(task['score'] for task in tasks) / len(tasks)
    skill_score = sum(skill['score'] for skill in skills) / len(skills)
    
    return (task_score + skill_score) / 2

# ❌ 避免的代码
def calc(t,s):return(t+s)/2
```

### 命名规范

- **类名**: PascalCase (`TaskPerformanceAnalyzer`)
- **函数/方法**: snake_case (`analyze_all_tasks`)
- **常量**: UPPER_CASE (`MAX_RECOMMENDATIONS`)
- **私有方法**: 前缀下划线 (`_internal_method`)

### 文档字符串

所有公共函数和类必须包含文档字符串：

```python
def generate_report(format='markdown'):
    """
    生成进化报告
    
    Args:
        format (str): 报告格式 ('markdown' 或 'json')
    
    Returns:
        str: 格式化的报告内容
    
    Raises:
        ValueError: 当 format 参数无效时
    """
    if format not in ['markdown', 'json']:
        raise ValueError("Format must be 'markdown' or 'json'")
    
    # 实现代码
```

---

## ✅ 测试要求

### 1. 单元测试

每个新功能必须包含单元测试：

```python
def test_health_score_calculation():
    """测试健康分数计算"""
    tasks = [{'score': 80}, {'score': 90}]
    skills = [{'score': 85}]
    
    score = calculate_health_score(tasks, skills)
    
    assert score == 85.0
```

### 2. 测试覆盖率

- 新功能覆盖率必须 >90%
- 整体项目覆盖率保持 >85%

```bash
# 运行测试并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 3. 测试命名

```python
def test_<function>_<scenario>_<expected_result>():
    """测试函数_场景_预期结果"""
    pass

# 示例
def test_analyze_tasks_empty_list_returns_zero():
    pass

def test_calculate_score_negative_values_raises_error():
    pass
```

---

## 📚 文档规范

### README 更新

新功能需要更新 README：

- 在相应章节添加说明
- 提供使用示例
- 包含必要的配置说明

### API 文档

公共 API 需要完整文档：

```markdown
## TaskPerformanceAnalyzer

### analyze_all_tasks()

分析所有任务的执行数据。

**返回值**:
- `dict`: 包含以下字段：
  - `total_tasks` (int): 总任务数
  - `success_rate` (float): 成功率
  - `health_score` (int): 健康分数 (0-100)

**示例**:
```python
analyzer = TaskPerformanceAnalyzer()
analysis = analyzer.analyze_all_tasks()
```
```

---

## 🚀 发布流程

### 版本号规范

遵循 [Semantic Versioning](https://semver.org/)：

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的新功能
- **PATCH**: 向后兼容的 Bug 修复

### 发布步骤

1. 更新版本号 (`pyproject.toml`)
2. 更新 CHANGELOG.md
3. 创建 Release Tag
4. 发布到 PyPI
5. 发布 GitHub Release

---

## 🎯 代码审查清单

提交 PR 前请自查：

- [ ] 代码通过所有测试
- [ ] 代码格式化（black）
- [ ] 代码风格检查通过（flake8）
- [ ] 添加了必要的测试
- [ ] 更新了文档
- [ ] 没有无关的更改
- [ ] 提交信息清晰规范

---

## 📞 联系方式

- **GitHub Issues**: https://github.com/yadadinae/agent-evolution/issues
- **Email**: support@studyai.ltd
- **讨论区**: https://github.com/yadadinae/agent-evolution/discussions

---

感谢你的贡献！🎉
