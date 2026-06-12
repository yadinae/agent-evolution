"""Agent Evolution — 基础测试套件

运行: python3 -m pytest tests/ -v
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# 加入项目路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "v2"))

# ─── Test: v2/daily_analysis.py 的独立函数 ───────

def test_import_daily_analysis():
    """验证 v2 分析器可以导入"""
    import daily_analysis
    assert hasattr(daily_analysis, "CronHealthAnalyzer")
    assert hasattr(daily_analysis, "SkillsQualityAudit")
    assert hasattr(daily_analysis, "GitChangeAnalyzer")
    assert hasattr(daily_analysis, "EvolutionReportGenerator")


# ─── Test: evolve_analysis.py 的配置兼容性 ───────

def test_evolve_analysis_config():
    """验证 evolve_analysis.py 使用环境变量配置路径"""
    # 设置测试 WORKSPACE
    with tempfile.TemporaryDirectory() as td:
        old_ws = os.environ.get("AGENT_EVOLUTION_WORKSPACE")
        os.environ["AGENT_EVOLUTION_WORKSPACE"] = td
        try:
            # 模拟 import 并检查路径
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "evolve_analysis",
                str(PROJECT_ROOT / "evolve_analysis.py")
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                # 只加载配置部分，不执行 main
                exec(open(spec.origin).read()[:40], mod.__dict__)
                assert hasattr(mod, "WORKSPACE")
                assert str(mod.WORKSPACE) == td
        finally:
            if old_ws:
                os.environ["AGENT_EVOLUTION_WORKSPACE"] = old_ws
            else:
                os.environ.pop("AGENT_EVOLUTION_WORKSPACE", None)


# ─── Test: mcp_server.js 的 tool 定义 ───────

def test_mcp_tool_registration():
    """验证 MCP 服务的工具数量"""
    import subprocess
    import json

    proc = subprocess.run(
        ["node", "-e", """
const s = require('child_process').spawn('node', ['mcp_server.js'], {
  cwd: process.argv[1], stdio: ['pipe', 'pipe', 'pipe']
});
let buf = '';
s.stdout.on('data', d => buf += d);
s.on('close', () => {
  const lines = buf.trim().split('\\n').filter(l => l.startsWith('{'));
  if (lines.length > 0) process.stdout.write(lines[lines.length - 1]);
});
s.stdin.write(JSON.stringify({jsonrpc:'2.0',id:1,method:'tools/list',params:{}}) + '\\n');
s.stdin.end();
setTimeout(() => process.exit(0), 3000);
""", str(PROJECT_ROOT)],
        capture_output=True, text=True, timeout=10,
        cwd=PROJECT_ROOT,
    )

    if proc.stdout.strip():
        result = json.loads(proc.stdout.strip())
        tools = result.get("result", {}).get("tools", [])
        tool_names = [t["name"] for t in tools]
        assert "analyze_system" in tool_names
        assert "audit_skills" in tool_names
        assert "check_cron" in tool_names
        assert "run_gep" in tool_names
        assert "get_evolution_history" in tool_names
        assert len(tools) >= 5
