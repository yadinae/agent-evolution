#!/usr/bin/env node
/**
 * Agent Evolution MCP Server
 * 
 * Exposes agent-evolution capabilities as MCP tools.
 * Any MCP-compatible agent (Hermes, Claude Code, etc.) can use these tools.
 * 
 * Run: node mcp_server.js
 * Transport: stdio (MCP standard)
 */

const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');
const {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} = require('@modelcontextprotocol/sdk/types.js');
const { execSync, spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// --- Config ---
const SERVER_ROOT = __dirname;
const V2_DIR = path.join(SERVER_ROOT, 'v2');
const PYTHON = '/usr/bin/python3';

// --- Helper: run Python script and return JSON ---
function runPython(scriptPath, args = []) {
  return new Promise((resolve, reject) => {
    const proc = spawn(PYTHON, [scriptPath, ...args], {
      cwd: SERVER_ROOT,
      timeout: 60000,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', (d) => { stdout += d.toString(); });
    proc.stderr.on('data', (d) => { stderr += d.toString(); });
    proc.on('close', (code) => {
      if (code === 0) {
        // Try to extract JSON from output
        const jsonMatch = stdout.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          try {
            resolve(JSON.parse(jsonMatch[0]));
          } catch (e) {
            resolve({ raw: stdout.trim(), stderr: stderr.trim() });
          }
        } else {
          resolve({ raw: stdout.trim(), stderr: stderr.trim() });
        }
      } else {
        reject(new Error(`Exit ${code}: ${stderr.trim() || stdout.trim()}`));
      }
    });
    proc.on('error', reject);
  });
}

// --- Helper: read generated report file ---
function readLatestOutput(suffix) {
  const outputDir = path.join(V2_DIR, 'output');
  if (!fs.existsSync(outputDir)) return null;
  const files = fs.readdirSync(outputDir)
    .filter(f => f.endsWith(suffix))
    .sort()
    .reverse();
  if (files.length === 0) return null;
  const content = fs.readFileSync(path.join(outputDir, files[0]), 'utf-8');
  return { file: files[0], content };
}

// --- Tool Implementations ---

async function toolAnalyzeSystem(args) {
  try {
    const result = await runPython(path.join(V2_DIR, 'daily_analysis.py'), []);
    // Also read the generated report
    const report = readLatestOutput('.md');
    const plan = readLatestOutput('-plan.json');
    const data = readLatestOutput('-data.json');
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          summary: result,
          report: report ? { file: report.file, excerpt: report.content.slice(0, 3000) } : null,
          plan: plan ? JSON.parse(plan.content) : null,
          data: data ? JSON.parse(data.content) : null,
        }, null, 2),
      }],
    };
  } catch (e) {
    return { content: [{ type: 'text', text: `分析失败: ${e.message}` }], isError: true };
  }
}

async function toolAuditSkills(args) {
  // Run hermes-scan.py for skill data, then parse
  try {
    const scan = execSync(`${PYTHON} ~/.hermes/bin/hermes-scan.py 2>/dev/null`, {
      timeout: 30000, encoding: 'utf-8',
    });
    const scanData = JSON.parse(scan);
    const skills = scanData.skills || {};
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          total: skills.total,
          with_doc: skills.with_doc,
          without_doc: skills.without_doc,
          missing: skills.missing,
          by_category: skills.by_category,
          status: skills.status,
        }, null, 2),
      }],
    };
  } catch (e) {
    return { content: [{ type: 'text', text: `技能审计失败: ${e.message}` }], isError: true };
  }
}

async function toolCheckCron(args) {
  try {
    const scan = execSync(`${PYTHON} ~/.hermes/bin/hermes-scan.py 2>/dev/null`, {
      timeout: 30000, encoding: 'utf-8',
    });
    const scanData = JSON.parse(scan);
    const cron = scanData.cron || {};
    const config = scanData.cron_config || {};
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          total: cron.total_jobs,
          jobs: cron.jobs,
          config_issues: config.config_issues,
        }, null, 2),
      }],
    };
  } catch (e) {
    return { content: [{ type: 'text', text: `Cron 检查失败: ${e.message}` }], isError: true };
  }
}

async function toolRunGep(args) {
  const evolveScript = path.join(SERVER_ROOT, 'src', 'evolve.js');
  if (!fs.existsSync(evolveScript)) {
    return { content: [{ type: 'text', text: 'GEP 引擎未找到，需要先安装 Node.js 依赖' }], isError: true };
  }
  try {
    const mode = args.mode || 'analyze';
    const strategy = args.strategy || 'balanced';
    const signals = args.signals ? (Array.isArray(args.signals) ? args.signals : [args.signals]) : [];
    
    // Set up env for GEP
    const env = { ...process.env, EVOLVE_STRATEGY: strategy };
    if (signals.length > 0) {
      env.EVOLVE_SIGNALS = JSON.stringify(signals);
    }
    
    const nodePath = process.env.NODE_PATH || path.join(SERVER_ROOT, 'node_modules');
    const result = execSync(`NODE_PATH=${nodePath} node ${evolveScript} --${mode}`, {
      cwd: SERVER_ROOT, timeout: 60000, encoding: 'utf-8', env,
    });
    return {
      content: [{ type: 'text', text: result.trim() || `GEP ${mode} 完成（无输出）` }],
    };
  } catch (e) {
    return { content: [{ type: 'text', text: `GEP 执行失败: ${e.message}` }], isError: true };
  }
}

async function toolGetEvolutionHistory(args) {
  const days = args.days || 7;
  const outputDir = path.join(V2_DIR, 'output');
  if (!fs.existsSync(outputDir)) {
    return { content: [{ type: 'text', text: '无进化历史数据' }] };
  }
  const cutoff = Date.now() - days * 86400000;
  const reports = fs.readdirSync(outputDir)
    .filter(f => f.endsWith('.md') || f.endsWith('-report.json'))
    .filter(f => {
      try {
        const stat = fs.statSync(path.join(outputDir, f));
        return stat.mtimeMs > cutoff;
      } catch { return false; }
    })
    .sort()
    .reverse()
    .slice(0, 10);
  return {
    content: [{ type: 'text', text: JSON.stringify({ days, report_count: reports.length, reports }, null, 2) }],
  };
}

// --- Tool Definitions ---
const TOOLS = [
  {
    name: 'analyze_system',
    description: '对 Hermes 系统进行全面进化分析。运行 v2 分析器，输出 Cron 健康、技能库质量、Git 活动、改进计划等结构化数据。返回包含摘要报告和 JSON 数据的完整分析结果。',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
  {
    name: 'audit_skills',
    description: '审计 Hermes 技能库质量。返回技能总数、有文档比例、缺文档清单、按分类分布等数据。基于 hermes-scan.py 实时采集。',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
  {
    name: 'check_cron',
    description: '检查 Hermes cron 任务运行健康状态。返回各任务最新运行时间、配置问题、toolset 限制等。基于 hermes-scan.py 实时采集。',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
  {
    name: 'run_gep',
    description: '运行 GEP（遗传进化协议）引擎。支持 analyze/fix/innovate 模式。需要 Node.js 环境和 GEP 模块。strategy 参数可选值: balanced, innovate, harden, repair-only, early-stabilize, steady-state, auto',
    inputSchema: {
      type: 'object',
      properties: {
        mode: {
          type: 'string',
          description: '运行模式: analyze（分析）, fix（修复）, innovate（创新）',
          enum: ['analyze', 'fix', 'innovate'],
        },
        strategy: {
          type: 'string',
          description: '进化策略',
          enum: ['balanced', 'innovate', 'harden', 'repair-only', 'early-stabilize', 'steady-state', 'auto'],
        },
        signals: {
          type: 'array',
          items: { type: 'string' },
          description: '触发信号列表（如 cron_error, skill_docs_missing, disk_high）',
        },
      },
    },
  },
  {
    name: 'get_evolution_history',
    description: '获取最近 N 天的进化分析历史记录列表。返回报告文件清单和基本信息。',
    inputSchema: {
      type: 'object',
      properties: {
        days: {
          type: 'number',
          description: '回溯天数（默认 7）',
        },
      },
    },
  },
];

// --- MCP Server ---
const server = new Server(
  { name: 'agent-evolution', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  switch (name) {
    case 'analyze_system':    return await toolAnalyzeSystem(args);
    case 'audit_skills':      return await toolAuditSkills(args);
    case 'check_cron':        return await toolCheckCron(args);
    case 'run_gep':           return await toolRunGep(args);
    case 'get_evolution_history': return await toolGetEvolutionHistory(args);
    default:
      return { content: [{ type: 'text', text: `未知工具: ${name}` }], isError: true };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // stderr log won't interfere with stdio MCP protocol
  console.error('[AgentEvolution MCP] Server started on stdio');
}

main().catch((e) => {
  console.error('[AgentEvolution MCP] Fatal:', e);
  process.exit(1);
});
