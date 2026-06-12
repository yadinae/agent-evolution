# Agent Evolution — 快速开始

## 环境要求

| 依赖 | 版本 | 说明 |
|:-----|:----|:------|
| Node.js | >= 18 | 运行 GEP 引擎和 MCP 服务 |
| Python | >= 3.6 | 运行分析脚本（v2 daily_analysis, evolve_analysis） |

## 安装

```bash
git clone https://github.com/yadinae/agent-evolution.git
cd agent-evolution

# JS 依赖（MCP 服务）
npm install

# Python 依赖
pip install -r requirements.txt
```

## 环境变量

| 变量 | 默认值 | 说明 |
|:-----|:-------|:------|
| `HERMES_HOME` | `~/.hermes` | Hermes 根目录 |
| `AGENT_EVOLUTION_WORKSPACE` | `$HERMES_HOME` | 工作空间路径 |
| `EVOLVE_STRATEGY` | `balanced` | GEP 策略: balanced / innovate / harden / repair-only / early-stabilize / steady-state / auto |

## 运行方式

### 1. 每日分析（Python）
```bash
python3 v2/daily_analysis.py
# 输出: v2/output/evolution-report-YYYY-MM-DD.md
```

### 2. 完整进化分析
```bash
python3 evolve_analysis.py --analyze
```

### 3. GEP 遗传进化引擎（Node.js）
```bash
# 单次分析
node src/evolve.js --analyze

# 持续循环
node src/evolve.js --loop
```

### 4. MCP 服务（供 Agent 调用）
```bash
node mcp_server.js
# 启动后通过 MCP stdio 协议提供 5 个工具
```

### 5. Hermes Cron 集成
配置已在 Hermes config.yaml 中添加：
```yaml
mcp_servers:
  agent-evolution:
    command: "node"
    args: ["~/projects/agent-evolution/mcp_server.js"]
    timeout: 120
```

## 架构说明

```
agent-evolution/
├── evolve_analysis.py      # 完整进化分析（Python, 1868行）
├── mcp_server.js           # MCP 服务（5 tools）
├── v2/
│   ├── daily_analysis.py   # 每日快速分析（525行）
│   └── hermes_self_analyzer.py  # 自我分析器（1065行）
├── src/
│   ├── evolve.js           # GEP 主引擎（1405行）
│   ├── gep/                # 遗传进化协议模块
│   └── ops/                # 运维操作（self_repair, health_check 等）
└── scripts/
    ├── evolve.sh           # 命令行入口
    └── index.js            # Node.js 入口
```
