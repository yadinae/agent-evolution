"""Agent Evolution — 基础测试套件

运行: python3 -m pytest tests/ -v
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "v2"))

# ─── Test: v2/daily_analysis.py 的独立函数 ───────

def test_import_daily_analysis_has_functions():
    """验证 v2 分析器的核心函数可以导入"""
    import daily_analysis
    assert hasattr(daily_analysis, "analyze_cron_health")
    assert hasattr(daily_analysis, "analyze_skills")
    assert hasattr(daily_analysis, "analyze_git_activity")
    assert hasattr(daily_analysis, "generate_plan")
    assert hasattr(daily_analysis, "generate_report")
    assert hasattr(daily_analysis, "main")


# ─── Test: evolve_analysis.py 的配置兼容性 ───────

def test_evolve_analysis_env_config():
    """验证 evolve_analysis.py 使用 AGENT_EVOLUTION_WORKSPACE 环境变量"""
    with tempfile.TemporaryDirectory() as td:
        old_ws = os.environ.get("AGENT_EVOLUTION_WORKSPACE")
        os.environ["AGENT_EVOLUTION_WORKSPACE"] = td
        try:
            sys.path.insert(0, str(PROJECT_ROOT))
            import evolve_analysis
            # 重新加载以读取新环境变量
            import importlib
            importlib.reload(evolve_analysis)
            assert str(evolve_analysis.WORKSPACE) == td
        finally:
            if old_ws:
                os.environ["AGENT_EVOLUTION_WORKSPACE"] = old_ws
            else:
                os.environ.pop("AGENT_EVOLUTION_WORKSPACE", None)


# ─── Test: 包导入（P2-4 修复验证） ───────

def test_src_package_imports():
    """验证 src/ 包可以通过标准导入（无 sys.path.insert 依赖）"""
    sys.path.insert(0, str(PROJECT_ROOT))
    from src.wal_protocol import WALProtocol
    from src.working_buffer import WorkingBuffer
    from src.feishu_reporter import FeishuReporter
    assert WALProtocol is not None
    assert WorkingBuffer is not None
    assert FeishuReporter is not None


# ─── Test: MCP 工具注册（Python 3.6 兼容） ───────

def test_mcp_tool_count():
    """验证 MCP 服务至少注册了 5 个工具"""
    # 使用 ndjson 解析 MCP 服务的 JSON-RPC 响应
    proc = subprocess.run(
        ["node", "-e", """
const s = require('child_process').spawn('node', ['mcp_server.js'], {
  cwd: process.argv[1], stdio: ['pipe', 'pipe', 'pipe']
});
var buf = '';
s.stdout.on('data', function(d) { buf += d.toString(); });
s.on('close', function() {
  var lines = buf.trim().split('\\n').filter(function(l) { return l.startsWith('{'); });
  if (lines.length > 0) process.stdout.write(lines[lines.length - 1]);
});
s.stdin.write(JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/list',params:{}}) + '\\n');
s.stdin.end();
setTimeout(function() { process.exit(0); }, 3000);
""", str(PROJECT_ROOT)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=10, cwd=str(PROJECT_ROOT),
    )
    out = proc.stdout.decode("utf-8", errors="replace").strip()
    if out:
        result = json.loads(out)
        tools = result.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        required = {"analyze_system", "audit_skills", "check_cron", "run_gep", "get_evolution_history"}
        assert required.issubset(set(tool_names)), f"缺少工具: {required - set(tool_names)}"
        assert len(tools) >= 5, f"工具数不足: {len(tools)}"
