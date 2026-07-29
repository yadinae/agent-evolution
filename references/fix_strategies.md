# Fix Strategies — Agent Evolution 修复策略映射表

> 将 `session_analyzer.py` 检测到的错误签名映射为可执行的修复动作。
> 供 `evolve_analysis.py` 在生成改进计划时使用。

## 使用方法

Agent Evolution 的分析流程：

```
session_analyzer 检测错误 → 分类为 category → lookup fix strategy →
generate patch指令 / GEP 进化 → apply → verify
```

每个修复策略包含：
- **detect**: `session_analyzer.py` 检测到的错误模式
- **category**: 错误分类（和 `ERROR_SIGNATURES` 中的 category 一致）
- **root cause**: 根因分析
- **fix**: 具体修复动作
- **template**: 可复用的 patch 模板
- **priority**: 建议优先级
- **verify**: 如何验证修复生效

---

## 1️⃣ 错误修复策略

### 1.1 `command_not_found` — 命令不存在

| 字段 | 内容 |
|------|------|
| **detect** | `"command not found"` |
| **root cause** | 执行 shell 命令前未检查目标命令是否在 PATH 中 |
| **fix** | 在调用终端命令前加 `which` / `command -v` 检查 |
| **priority** | P1（高频阻塞工具） |

**Patch template (SKILL.md 追加):**
```markdown
## Pre-flight Checks (command_not_found)
在调用 `terminal()` 执行任何命令前，先执行 which/command -v 检查：
```
# 安全执行模式
cmd_exists() { command -v "$1" >/dev/null 2>&1; }
if ! cmd_exists "ffmpeg"; then
  echo "❌ ffmpeg not found. Install: apt install ffmpeg"
  # 尝试降级方案
fi
```
```

**Verify**: 命令不存在时给出清晰的安装提示而非原始错误。

---

### 1.2 `path_not_found` — 路径不存在

| 字段 | 内容 |
|------|------|
| **detect** | `"No such file"`, `"no such file or directory"`, `"ENOENT"` |
| **root cause** | 文件/目录路径未经验证直接操作 |
| **fix** | 在读写/切换目录前先 `os.path.exists()` 检查 |
| **priority** | P1 |

**Patch template (SKILL.md 追加):**
```markdown
## Pre-flight Checks (path_not_found)
在 ANY 文件操作前验证路径存在：
```
import os
path = "/some/path"
if not os.path.exists(path):
    # 尝试常见替代路径
    alt_paths = [os.path.expanduser(f"~/{path}"), os.path.join(os.getcwd(), path)]
    for alt in alt_paths:
        if os.path.exists(alt):
            path = alt
            break
    else:
        raise FileNotFoundError(f"Path not found: {path}")
```
```

**Verify**: 路径不存在时自动搜索替代路径而非报错退出。

---

### 1.3 `permission` — 权限不足

| 字段 | 内容 |
|------|------|
| **detect** | `"permission denied"`, `"EACCES"`, `"access denied"` |
| **root cause** | 当前用户对目标文件/目录没有读写执行权限 |
| **fix** | 检查权限、提示修正命令、尝试读替代路径 |
| **priority** | P1 |

**Patch template (SKILL.md 追加):**
```markdown
## Permission Handling
```
import os, stat

def safe_read(path):
    if not os.access(path, os.R_OK):
        # 提示用户修正
        print(f"🔒 Permission denied: {path}")
        print(f"   → chmod +r {path} 或 sudo 执行")
        # 尝试读取相同目录下其他文件
        alt = os.path.join(os.path.dirname(path), "..", os.path.basename(path))
        if os.path.exists(alt) and os.access(alt, os.R_OK):
            return open(alt).read()
        raise PermissionError(f"Cannot read {path}")
    return open(path).read()
```
```

**Verify**: 权限不足时给出具体的 `chmod`/`chown` 建议而非裸错误。

---

### 1.4 `timeout` — 超时

| 字段 | 内容 |
|------|------|
| **detect** | `"timeout"`, `"ETIMEDOUT"` |
| **root cause** | 网络请求/外部命令执行超时，无重试和退避策略 |
| **fix** | 增加重试逻辑：指数退避 + 最大重试次数 |
| **priority** | P1（最普遍的工具失败原因） |

**Patch template:**
```markdown
## Retry with Exponential Backoff
```
import time, random

def with_retry(fn, max_retries=3, base_delay=2):
    for attempt in range(max_retries):
        try:
            return fn()
        except (TimeoutError, ConnectionError) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"⏳ Retry {attempt+1}/{max_retries} after {delay:.1f}s ({e})")
            time.sleep(delay)
    return None
```
```

**Verify**: 网络操作在超时后自动重试 3 次，最终失败时提供降级选项。

---

### 1.5 `connection` — 连接拒绝

| 字段 | 内容 |
|------|------|
| **detect** | `"connection refused"` |
| **root cause** | 目标服务未运行或端口不可达 |
| **fix** | 检查服务存活 + 重试 + 降级 |
| **priority** | P1 |

**Patch template:**
```markdown
## Connection Handling
```
def connect_with_check(host, port, timeout=5):
    import socket
    # 先检查端口是否开放
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        if result != 0:
            print(f"🔌 Port {port} on {host} is closed (code={result})")
            return None
    finally:
        sock.close()
    # 端口开放后再建立实际连接
    return actual_connect(host, port)
```
```

**Verify**: 连接失败时提示服务未运行而非静默崩溃。

---

### 1.6 `rate_limit` — 速率限制

| 字段 | 内容 |
|------|------|
| **detect** | `"rate limit"`, `"429 Too Many Requests"` |
| **root cause** | 短时间内请求过多触发 API 限流 |
| **fix** | 请求队列 + 退避策略 + 降低并发 |
| **priority** | P1 |

**Patch template:**
```markdown
## Rate Limiting
```
import time
from collections import deque

class RateLimiter:
    def __init__(self, max_per_minute=30):
        self.requests = deque()
        self.max_per_minute = max_per_minute

    def wait(self):
        now = time.time()
        # 清理过期记录
        while self.requests and now - self.requests[0] > 60:
            self.requests.popleft()
        if len(self.requests) >= self.max_per_minute:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                print(f"⏱️ Rate limit: waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)
        self.requests.append(time.time())

limiter = RateLimiter(max_per_minute=20)
limiter.wait()  # 每次 API 调用前调用
```
```

**Verify**: 限流发生时自动等待而非直接失败。

---

### 1.7 `not_found` — 404/资源不存在

| 字段 | 内容 |
|------|------|
| **detect** | `"404 Not Found"` |
| **root cause** | URL 错误、资源已被删除、ID 过期 |
| **fix** | 验证 URL 格式 + 尝试替代路径/搜索 |
| **priority** | P2 |

**Patch template:**
```markdown
## Not Found Handling
```
def fetch_with_fallback(url):
    import re
    # URL 格式校验
    if not re.match(r'^https?://', url):
        url = f"https://{url}"
    try:
        return fetch(url)
    except HTTPError as e:
        if e.code == 404:
            # 尝试搜索
            search_query = url.split('/')[-1].replace('-', ' ')
            results = web_search(search_query)
            if results:
                return results[0].url
        raise
```
```

---

### 1.8 `server_error` — 服务端 5xx

| 字段 | 内容 |
|------|------|
| **detect** | `"500 Internal Server"`, `"502 Bad Gateway"`, `"503 Service Unavailable"` |
| **root cause** | 上游服务崩溃或正在重启 |
| **fix** | 重试 + 降级到缓存/替代数据源 |
| **priority** | P2 |

**Patch template:**
```markdown
## Server Error Handling
```
@with_retry(max_retries=3)
def safe_api_call(url):
    resp = requests.get(url, timeout=10)
    if resp.status_code >= 500:
        # 尝试缓存
        cache_key = f"cache_{hash(url)}"
        if cache_key in local_cache:
            return local_cache[cache_key]
        resp.raise_for_status()
    return resp.json()
```
```

---

### 1.9 `auth` — 认证失败

| 字段 | 内容 |
|------|------|
| **detect** | `"unauthorized"`, `"401"` |
| **root cause** | API Key 过期、token 无效、缺少认证头 |
| **fix** | 自动刷新 token + 明确的错误提示 |
| **priority** | P0 |

**Patch template:**
```markdown
## Auth Handling
```
def refresh_if_needed(fn):
    """如果 401，自动尝试刷新 token 后重试"""
    try:
        return fn()
    except HTTPError as e:
        if e.code == 401:
            refresh_token()
            return fn()  # 重试
        raise

# 在 SKILL.md 中提供必要的认证配置说明
```
>>> REQUIRED CONFIG:
>>> - API_KEY / ACCESS_TOKEN 从环境变量或 .env 读取
>>> - 不要在代码中硬编码密钥
```

**Verify**: 认证失败时给出具体的环境变量名称而非笼统的 "auth error"。

---

### 1.10 `syntax_error` — 语法错误

| 字段 | 内容 |
|------|------|
| **detect** | `"syntax error"` |
| **root cause** | 生成的命令/代码包含拼写或语法错误 |
| **fix** | 生成代码后先用语法检查再执行 |
| **priority** | P2 |

**Patch template:**
```markdown
## Syntax Validation
```
import ast, py_compile, tempfile

def validate_python(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError as e:
        print(f"📝 Syntax error in generated code: {e}")
        return False

def validate_shell(cmd: str) -> bool:
    """基本 shell 语法检查"""
    dangerous = ['rm -rf /', '> /dev/sda', 'mkfs']
    for d in dangerous:
        if d in cmd:
            print(f"⚠️ Dangerous command detected: {d}")
            return False
    return True
```
```

---

### 1.11 `missing_parameter` — 缺少参数

| 字段 | 内容 |
|------|------|
| **detect** | `"is required"`, `"missing required"`, `"must be provided"` |
| **root cause** | 工具调用时缺少必填参数 |
| **fix** | 调用前校验必填参数，缺失时自动补全或询问 |
| **priority** | P2 |

**Patch template:**
```markdown
## Parameter Validation
```
def validate_required(params, required_fields):
    missing = [f for f in required_fields if f not in params or params[f] is None]
    if missing:
        print(f"📋 Missing required params: {', '.join(missing)}")
        # 尝试从上下文推断
        for field in missing:
            inferred = infer_from_context(field)
            if inferred:
                params[field] = inferred
                print(f"  → Inferred {field}: {inferred}")
    return params
```
```

---

### 1.12 `runtime_error` — 运行时异常

| 字段 | 内容 |
|------|------|
| **detect** | `"Traceback"`, `"Exception:"` |
| **root cause** | 代码中存在未捕获的业务逻辑错误 |
| **fix** | 全局异常捕获 + 错误日志上下文记录 |
| **priority** | P2 |

**Patch template:**
```markdown
## Error Context Logging
```
import traceback

def safe_execute(fn, context=""):
    try:
        return fn()
    except Exception as e:
        error_ctx = {
            "error": str(e),
            "context": context,
            "traceback": traceback.format_exc(),
        }
        print(f"❌ [{context}] {e}")
        # 记录到 Hermes memory
        memory.add(f"failure_context", error_ctx)
        raise
```
```

---

## 2️⃣ 用户纠正修复策略

`session_analyzer.py` 检测到的用户纠正模式，映射为改进建议：

| 纠正模式 | 根因 | 修复策略 | 优先级 |
|----------|------|----------|--------|
| `"不对"` / `"错了"` | Agent 执行方向错误 | 在执行前加 **确认步骤**（ask before act） | P1 |
| `"不是这个"` / `"我说的是"` | 意图理解偏差 | 添加 **意图消歧**，让用户确认选项 | P1 |
| `"为什么"` / `"谁让你"` | 非预期操作 | 限制自动操作的权限范围 | P0 |
| `"停止"` / `"stop"` | 执行了不应执行的操作 | 添加安全阀：敏感操作前必须获明确确认 | P0 |
| `"wrong"` / `"incorrect"` | 输出内容错误 | 改进技能指令，减少幻觉产出 | P2 |
| `"try again"` / `"重试"` | 非指定性失败 | 提供更多上下文和选项 | P2 |

**通用修复模板：**
```markdown
## Correction Prevention
执行可能产生副作用的操作前：
1. 先用 `clarify` 确认用户意图（如果模糊）
2. 对文件修改操作先 dry-run 展示 diff
3. 记录每次纠正到技能 memory 避免重复犯错
```

---

## 3️⃣ 技能缺口创建策略

`session_analyzer.py` 检测到的高频需求但无对应技能：

| 能力缺口 | 出现频率阈值 | 自动创建模板 | 分类 |
|----------|-------------|-------------|------|
| 网络请求 | ≥ 3 次 | 基础的 HTTP fetch 技能 | devops |
| CSV/Excel | ≥ 3 次 | CSV 解析 + pandas 处理 | data-science |
| 部署 | ≥ 3 次 | 部署流水线脚本 | devops |
| 文件批量 | ≥ 3 次 | 批量文件操作（glob + loop） | devops |
| 数据分析 | ≥ 5 次 | 数据清洗 + 可视化 | data-science |
| 定时任务 | ≥ 5 次 | cron 配置 + 任务编排 | devops |
| 数据库 | ≥ 3 次 | SQLite/Postgres 查询封装 | devops |
| 图片处理 | ≥ 3 次 | Pillow 基础操作 | creative |

**通用技能创建模板：**
```markdown
---
name: {skill_id}
description: 满足用户对{capability}的需求
category: {category}
---

# {capability}

## 触发条件

当用户请求涉及「{capability}」相关内容时自动调用。

## 标准流程

1. 确认用户具体需求（如果模糊就用 clarify）
2. 加载相关配置
3. 执行核心操作
4. 验证结果
5. 报告完成

## 已知陷阱

- {pitfall_1}
- {pitfall_2}

## 错误处理

- {error_1} → 重试 / 降级 / 提示
- {error_2} → 重试 / 降级 / 提示
```

---

## 4️⃣ 重试循环修复策略

`session_analyzer.py` 检测到同一工具 30 秒内 ≥4 次调用：

| 重试模式 | 根因 | 修复策略 | 优先级 |
|----------|------|----------|--------|
| `terminal` 重试循环 | 命令在短时间内反复执行失败 | 加 `--max-attempts 3` 和冷却间隔 | P1 |
| `read_file` 重试循环 | 递归读取多个文件 | 改用 `search_files` + 批量读取 | P2 |
| `web_search`/`web_extract` 重试 | 网络不稳定 | 加退避 + 降级到备用工具 | P1 |
| `execute_code` 重试循环 | 代码反复报错 | 先检查语法，再用二分定位错误 | P2 |

**通用修复模板：**
```markdown
## Retry Loop Prevention
- 用 `with_retry()` 替代裸调用
- 每次调用间至少等待 0.5s
- 连续失败 3 次后改用替代方案
- 记录错误模式到 memory 避免下次重蹈覆辙
```

---

## 5️⃣ 附录：策略索引

### 按优先级排序

| 优先级 | 策略 | 说明 |
|--------|------|------|
| **P0** | `auth` | 认证问题需要立即修复，否则工具完全不可用 |
| **P1** | `timeout`, `command_not_found`, `path_not_found`, `permission`, `connection`, `rate_limit` | 阻塞日常使用的高频错误 |
| **P2** | `not_found`, `server_error`, `syntax_error`, `missing_parameter`, `runtime_error` | 影响使用但不阻塞的错误 |

### 按工具分布

| 高频报错工具 | 最常见错误 | 适用策略 |
|-------------|-----------|----------|
| `terminal` | command_not_found, permission | 1.1, 1.3 |
| `web_extract` | timeout, connection | 1.4, 1.5 |
| `web_search` | rate_limit, timeout | 1.6, 1.4 |
| `read_file` | path_not_found, permission | 1.2, 1.3 |
| `execute_code` | runtime_error, syntax_error | 1.12, 1.10 |
| `patch` | path_not_found | 1.2 |
| `delegate_task` | timeout | 1.4 |

---

## 版本历史

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-07-02 | 1.0 | 初始版本，覆盖 12 类错误 + 用户纠正 + 技能缺口 + 重试循环 |

> 本文档由 Agent Evolution 的 `session_analyzer.py` + `evolve_analysis.py` 联合使用。
> 错误分类与 `session_analyzer.py` 的 `ERROR_SIGNATURES` 严格对应。
