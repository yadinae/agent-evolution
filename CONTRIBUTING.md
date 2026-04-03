# 贡献者指南 🤝

欢迎为 Agent Evolution 项目做出贡献！本指南将帮助你快速上手。

---

## 📖 目录

- [行为准则](#行为准则)
- [如何贡献](#如何贡献)
- [开发环境设置](#开发环境设置)
- [提交流程](#提交流程)
- [代码规范](#代码规范)
- [测试要求](#测试要求)
- [文档规范](#文档规范)
- [发布流程](#发布流程)
- [常见问题](#常见问题)

---

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或侮辱性评论
- 公开或私下骚扰
- 未经许可发布他人信息
- 其他不道德或不专业的行为

---

## 如何贡献

### 贡献方式

你可以通过以下方式贡献：

1. **报告 Bug** - 提交 Issue 描述问题
2. **建议功能** - 提交 Issue 提出新功能建议
3. **修复 Bug** - 提交 PR 修复已知问题
4. **实现功能** - 提交 PR 实现新功能
5. **改进文档** - 修正或补充文档
6. **代码审查** - 审查他人的 PR
7. **分享经验** - 撰写博客、教程

### 找到合适的任务

查看以下标签找到适合的任务：

- `good first issue` - 适合新手
- `help wanted` - 需要帮助
- `bug` - Bug 修复
- `enhancement` - 功能增强
- `documentation` - 文档改进

---

## 开发环境设置

### 1. Fork 仓库

在 GitHub 上点击 "Fork" 按钮创建你的 Fork。

### 2. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/agent-evolution.git
cd agent-evolution
```

### 3. 添加上游仓库

```bash
git remote add upstream https://github.com/yadinae/agent-evolution.git
git fetch upstream
```

### 4. 创建虚拟环境

```bash
# Python 3.11+
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

### 5. 安装依赖

```bash
# 安装开发依赖
pip install -r requirements.txt

# 安装开发工具
pip install black flake8 mypy pytest pytest-cov
```

### 6. 验证安装

```bash
# 运行测试
pytest tests/ -v

# 检查代码风格
flake8 src/ tests/

# 运行类型检查
mypy src/
```

---

## 提交流程

### 1. 创建功能分支

```bash
# 保持 main 分支最新
git checkout main
git pull upstream main

# 创建功能分支
git checkout -b feature/your-feature-name
```

### 分支命名规范

- `feature/xxx` - 新功能
- `bugfix/xxx` - Bug 修复
- `hotfix/xxx` - 紧急修复
- `docs/xxx` - 文档更新
- `refactor/xxx` - 代码重构
- `test/xxx` - 测试添加
- `chore/xxx` - 其他变更

### 2. 进行更改

进行修改并确保：

- ✅ 代码遵循规范
- ✅ 添加了测试
- ✅ 所有测试通过
- ✅ 文档已更新

### 3. 提交更改

```bash
# 添加更改
git add .

# 提交 (使用 Conventional Commits)
git commit -m "feat: add new feature"
```

### Commit Message 规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/)：

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Type 类型**:
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式 (不影响代码运行)
- `refactor`: 重构 (既不是新功能也不是 Bug 修复)
- `test`: 测试添加或修改
- `chore`: 构建过程或辅助工具变动

**示例**:
```
feat(task): add task performance analyzer

- Implement TaskPerformanceAnalyzer class
- Add 20 core metrics
- Create unit tests

Closes #123
```

### 4. 推送到分支

```bash
git push origin feature/your-feature-name
```

### 5. 创建 Pull Request

1. 访问你的 Fork 页面
2. 点击 "Compare & pull request"
3. 填写 PR 描述
4. 选择标签
5. 点击 "Create pull request"

---

## 代码规范

### Python 代码规范

遵循 [PEP 8](https://pep8.org/)：

```python
# ✅ 好的代码
def calculate_health_score(
    success_rate: float,
    avg_duration: float,
    error_rate: float
) -> float:
    """计算健康分数"""
    score = (
        success_rate * 0.4 +
        (1 - avg_duration / 100) * 0.3 +
        (1 - error_rate) * 0.3
    )
    return min(100, max(0, score * 100))

# ❌ 不好的代码
def calc(s,d,e):
    score=s*0.4+(1-d/100)*0.3+(1-e)*0.3
    return score
```

### 类型注解

所有公共函数必须有类型注解：

```python
# ✅ 好的代码
from typing import Dict, List, Optional

def analyze_tasks(
    task_ids: List[int],
    filters: Optional[Dict[str, str]] = None
) -> Dict[str, float]:
    """分析任务"""
    pass

# ❌ 不好的代码
def analyze_tasks(task_ids, filters=None):
    pass
```

### 文档字符串

所有公共函数和类必须有文档字符串：

```python
# ✅ 好的代码
class TaskAnalyzer:
    """任务分析器"""
    
    def analyze(self, task_id: int) -> Dict:
        """
        分析单个任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            分析结果字典
            
        Raises:
            ValueError: 如果任务 ID 无效
        """
        pass

# ❌ 不好的代码
class TaskAnalyzer:
    def analyze(self, task_id):
        pass
```

### 代码格式化

使用 Black 格式化代码：

```bash
# 安装 Black
pip install black

# 格式化代码
black src/ tests/

# 检查格式
black --check src/ tests/
```

### 代码检查

使用 flake8 检查代码风格：

```bash
# 安装 flake8
pip install flake8

# 检查代码
flake8 src/ tests/

# 忽略特定错误
flake8 src/ --ignore=E501,W503
```

### 类型检查

使用 mypy 进行类型检查：

```bash
# 安装 mypy
pip install mypy

# 类型检查
mypy src/

# 严格模式
mypy src/ --strict
```

---

## 测试要求

### 测试框架

使用 pytest 进行测试：

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_task_analyzer.py -v

# 运行带关键字的测试
pytest -k "test_health" -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 查看覆盖率
coverage report
```

### 测试编写规范

```python
# ✅ 好的测试
import pytest
from src.task_analyzer import TaskAnalyzer

class TestTaskAnalyzer:
    """TaskAnalyzer 测试类"""
    
    def test_analyze_success(self, sample_task):
        """测试成功分析任务"""
        analyzer = TaskAnalyzer()
        result = analyzer.analyze(sample_task['id'])
        
        assert result['status'] == 'success'
        assert 'metrics' in result
        assert result['metrics']['success_rate'] > 0
    
    def test_analyze_invalid_task(self):
        """测试分析无效任务"""
        analyzer = TaskAnalyzer()
        
        with pytest.raises(ValueError):
            analyzer.analyze(-1)

# ❌ 不好的测试
def test1():
    from src.task_analyzer import TaskAnalyzer
    a = TaskAnalyzer()
    r = a.analyze(1)
    assert r['status'] == 'success'
```

### 测试覆盖率要求

- **新功能**: 必须添加测试
- **覆盖率**: >90%
- **关键模块**: >95%

### 测试类型

1. **单元测试**: 测试单个函数或类
2. **集成测试**: 测试模块间交互
3. **性能测试**: 测试性能指标
4. **边界测试**: 测试边界条件
5. **错误处理测试**: 测试异常情况

---

## 文档规范

### 文档类型

1. **README.md**: 项目概述和快速开始
2. **API.md**: API 参考文档
3. **ARCHITECTURE.md**: 架构设计文档
4. **CONTRIBUTING.md**: 贡献指南
5. **CHANGELOG.md**: 变更日志
6. **Tutorials/**: 教程文档

### Markdown 规范

```markdown
# ✅ 好的标题

使用清晰的标题层级

## 二级标题

### 三级标题

#### 四级标题

# ✅ 好的代码块

```python
def example():
    """示例函数"""
    pass
```

# ✅ 好的列表

- 列表项 1
- 列表项 2
  - 子项 2.1
  - 子项 2.2

# ✅ 好的表格

| 列 1 | 列 2 | 列 3 |
|------|------|------|
| 值 1 | 值 2 | 值 3 |
| 值 4 | 值 5 | 值 6 |
```

### 文档更新要求

以下情况必须更新文档：

- ✅ 添加新功能
- ✅ 修改 API
- ✅ 变更配置
- ✅ 修复 Bug (如果影响行为)
- ✅ 性能优化 (如果改变使用方式)

---

## 发布流程

### 版本命名

遵循 [语义化版本 2.0.0](https://semver.org/)：

```
主版本号。次版本号。修订号
MAJOR.MINOR.PATCH
```

- **MAJOR**: 破坏性变更
- **MINOR**: 向后兼容的功能新增
- **PATCH**: 向后兼容的 Bug 修复

### 发布步骤

1. **更新版本号**
   ```python
   # src/__version__.py
   __version__ = "1.0.0"
   ```

2. **更新 CHANGELOG.md**
   ```markdown
   ## [1.0.0] - 2026-04-03
   
   ### Added
   - 新功能 1
   - 新功能 2
   
   ### Changed
   - 变更 1
   
   ### Fixed
   - Bug 修复 1
   ```

3. **创建 Git 标签**
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

4. **创建 GitHub Release**
   - 访问 Releases 页面
   - 创建新 Release
   - 使用 Release Drafter 生成说明
   - 发布

5. **发布到 PyPI** (如果适用)
   ```bash
   # 安装构建工具
   pip install build twine
   
   # 构建分发包
   python -m build
   
   # 上传到 PyPI
   twine upload dist/*
   ```

---

## 常见问题

### Q: 如何开始第一个贡献？

A: 从 `good first issue` 标签的任务开始，这些任务相对简单，适合新手。

### Q: 我的 PR 多久会被审查？

A: 通常在 1-3 个工作日内会有回应。如果超过 3 天，可以在 PR 中 @ 维护者。

### Q: 如何请求功能？

A: 在 Issues 中创建 "Feature Request"，详细描述功能需求和使用场景。

### Q: 如何报告 Bug？

A: 在 Issues 中创建 "Bug Report"，提供详细的复现步骤、期望行为和实际行为。

### Q: 我可以贡献文档吗？

A: 当然可以！文档贡献同样重要，欢迎任何文档改进。

### Q: 如何测试我的更改？

A: 运行 `pytest tests/ -v` 确保所有测试通过，并手动测试功能。

### Q: 代码风格检查失败怎么办？

A: 使用 `black` 格式化代码，根据 `flake8` 输出修复问题。

### Q: 如何添加测试？

A: 在 `tests/` 目录创建测试文件，遵循现有测试的结构和命名规范。

### Q: 我的 PR 被拒绝了怎么办？

A: 不要灰心！查看拒绝原因，进行修改后重新提交，或与维护者讨论。

### Q: 如何联系维护者？

A: 可以通过 Issue、PR 评论或邮件联系维护者。

---

## 贡献者权益

- ✅ 在 README 中列出贡献者
- ✅ 在发布说明中感谢贡献者
- ✅ 获得社区认可
- ✅ 提升技术能力
- ✅ 建立个人品牌

---

## 致谢

感谢所有为 Agent Evolution 项目做出贡献的开发者们！

你们的贡献让这个项目变得更好！🎉

---

*文档版本：1.0.0*  
*创建时间：2026-04-03*  
*最后更新：2026-04-03*
