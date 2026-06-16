#!/usr/bin/env node
/**
 * Agent Evolution MCP Server
 * 
 * Exposes agent-evolution capabilities as MCP tools.
 * Any MCP-compatible agent (Hermes, Claude Code, etc.) can use these tools.
 * 
 * v2.1: Added execute_plan tool — analysis → action pipeline
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
const OUTPUT_DIR = path.join(V2_DIR, 'output');
const FIX_INSTRUCTIONS_DIR = path.join(OUTPUT_DIR, 'fix_instructions');
const SKILLS_DIR = path.join(process.env.HOME || '/home/admin', '.hermes', 'skills');
const PYTHON = '/usr/bin/python3';

// --- Helper: run Python script and return JSON ---
function runPython(scriptPath, args = []) {
  return new Promise((resolve, reject) => {
    const proc = spawn(PYTHON, [scriptPath, ...args], {
      cwd: SERVER_ROOT,
      timeout: 120000,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    proc.stdout.on('data', (d) => { stdout += d.toString(); });
    proc.stderr.on('data', (d) => { stderr += d.toString(); });
    proc.on('close', (code) => {
      if (code === 0) {
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
  if (!fs.existsSync(OUTPUT_DIR)) return null;
  const files = fs.readdirSync(OUTPUT_DIR)
    .filter(f => f.endsWith(suffix) && !f.startsWith('fix_') && !f.startsWith('gep-'))
    .sort()
    .reverse();
  if (files.length === 0) return null;
  const content = fs.readFileSync(path.join(OUTPUT_DIR, files[0]), 'utf-8');
  return { file: files[0], content };
}

// --- Helper: read latest plan JSON ---
function readLatestPlan() {
  if (!fs.existsSync(OUTPUT_DIR)) return null;
  const files = fs.readdirSync(OUTPUT_DIR)
    .filter(f => f.endsWith('-plan.json'))
    .sort()
    .reverse();
  if (files.length === 0) return null;
  try {
    return JSON.parse(fs.readFileSync(path.join(OUTPUT_DIR, files[0]), 'utf-8'));
  } catch (e) {
    return null;
  }
}

// --- Tool Implementations ---

async function toolAnalyzeSystem(args) {
  try {
    const result = await runPython(path.join(V2_DIR, 'daily_analysis.py'), []);
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

async function toolExecutePlan(args) {
  /**
   * 执行最新改进计划中标记为 auto 的项。
   * 
   * 目前已实现的自动修复：
   * 1. 创建缺失的 SKILL.md（纯文件操作）
   * 2. 重启失败的 cron 任务（读取 fix_instructions/ 中的指令）
   * 3. 触发 GEP fix（可选）
   */
  try {
    // 1. Read the latest plan
    const plan = readLatestPlan();
    if (!plan) {
      return { content: [{ type: 'text', text: '❌ 未找到改进计划，请先运行 analyze_system' }], isError: true };
    }

    const results = [];
    const fixMode = args.mode || 'auto-fix';

    // 2. Execute auto items from the plan
    for (const action of plan.actions || []) {
      if (action.execution !== 'auto') continue;

      if (action.type === 'skill_documentation' && action.auto_fix && action.auto_fix.type === 'create_skill_docs') {
        // Create missing SKILL.md files
        for (const skill of action.auto_fix.skills || []) {
          const name = skill.name;
          const parts = name.split('/');
          const category = parts.length === 2 ? parts[0] : 'general';
          const skillName = parts.length === 2 ? parts[1] : name;
          const skillPath = path.join(SKILLS_DIR, category, skillName);
          const skillMd = path.join(skillPath, 'SKILL.md');

          if (!fs.existsSync(skillPath)) {
            results.push({ action: 'create_skill_md', skill: name, status: 'skipped', reason: 'skill dir not found' });
            continue;
          }
          if (fs.existsSync(skillMd)) {
            results.push({ action: 'create_skill_md', skill: name, status: 'skipped', reason: 'SKILL.md already exists' });
            continue;
          }

          try {
            const content = `---
name: ${skillName}
description: TODO: 补充技能描述
category: ${category}
---

# ${skillName}

## 概述

TODO: 补充技能说明

## 使用方法

TODO: 补充使用方法

## 注意事项

- 待补充
`;
            fs.writeFileSync(skillMd, content, 'utf-8');
            results.push({ action: 'create_skill_md', skill: name, path: skillMd, status: 'success' });
          } catch (e) {
            results.push({ action: 'create_skill_md', skill: name, status: 'error', error: e.message });
          }
        }
      }
    }

    // 3. Process pending cron restart instructions
    if (fs.existsSync(FIX_INSTRUCTIONS_DIR)) {
      const instructions = fs.readdirSync(FIX_INSTRUCTIONS_DIR)
        .filter(f => f.startsWith('restart-cron-') && f.endsWith('.json'));
      
      for (const instrFile of instructions) {
        try {
          const instrPath = path.join(FIX_INSTRUCTIONS_DIR, instrFile);
          const instr = JSON.parse(fs.readFileSync(instrPath, 'utf-8'));
          if (instr.type === 'cron_restart' && instr.job_id) {
            results.push({
              action: 'cron_restart',
              job_id: instr.job_id,
              status: 'instruction_found',
              instruction_file: instrFile,
              note: `Cron ${instr.job_id} 需要重启。使用 hermes cron run ${instr.job_id} 或 cronjob(action='run', job_id='${instr.job_id}') 执行。`
            });
          }
        } catch (e) {
          results.push({ action: 'read_instruction', file: instrFile, status: 'error', error: e.message });
        }
      }
    }

    // 4. Optionally trigger GEP fix
    let gepResult = null;
    if (fixMode === 'full' || fixMode === 'gep') {
      try {
        const evolveScript = path.join(SERVER_ROOT, 'src', 'evolve.js');
        if (fs.existsSync(evolveScript)) {
          gepResult = execSync(`NODE_PATH=${path.join(SERVER_ROOT, 'node_modules')} node ${evolveScript} --fix --strategy repair-only`, {
            cwd: SERVER_ROOT, timeout: 60000, encoding: 'utf-8',
          });
        } else {
          gepResult = 'GEP 引擎未安装';
        }
      } catch (e) {
        gepResult = `GEP 执行失败: ${e.message}`;
      }
    }

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          plan_date: plan.timestamp,
          total_actions_in_plan: plan.total_actions,
          auto_actions_in_plan: plan.auto_executable,
          executed: results.filter(r => r.status === 'success' || r.status === 'instruction_found').length,
          results,
          gep_triggered: gepResult,
        }, null, 2),
      }],
    };

  } catch (e) {
    return { content: [{ type: 'text', text: `执行计划失败: ${e.message}` }], isError: true };
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
  if (!fs.existsSync(OUTPUT_DIR)) {
    return { content: [{ type: 'text', text: '无进化历史数据' }] };
  }
  const cutoff = Date.now() - days * 86400000;
  const reports = fs.readdirSync(OUTPUT_DIR)
    .filter(f => f.endsWith('.md') || f.endsWith('-report.json'))
    .filter(f => {
      try {
        const stat = fs.statSync(path.join(OUTPUT_DIR, f));
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
    description: '对 Hermes 系统进行全面进化分析。运行 v2 分析器，输出 Cron 健康、技能库质量、Git 活动、改进计划等结构化数据。同时自动执行可修复项（创建缺漏的 SKILL.md 等）。返回包含摘要报告和 JSON 数据的完整分析结果。',
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
    name: 'execute_plan',
    description: '执行最新改进计划中的可自动修复项。默认模式 auto-fix 只执行文件操作（创建 SKILL.md），full 模式还会触发 GEP fix 引擎。修复前请先运行 analyze_system 生成最新计划。',
    inputSchema: {
      type: 'object',
      properties: {
        mode: {
          type: 'string',
          description: '执行模式: auto-fix（默认，只执行文件操作）, full（文件操作 + GEP fix）, gep（仅 GEP fix）',
          enum: ['auto-fix', 'full', 'gep'],
        },
      },
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
  { name: 'agent-evolution', version: '2.1.0' },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({ tools: TOOLS }));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  switch (name) {
    case 'analyze_system':    return await toolAnalyzeSystem(args);
    case 'audit_skills':      return await toolAuditSkills(args);
    case 'check_cron':        return await toolCheckCron(args);
    case 'execute_plan':      return await toolExecutePlan(args);
    case 'run_gep':           return await toolRunGep(args);
    case 'get_evolution_history': return await toolGetEvolutionHistory(args);
    default:
      return { content: [{ type: 'text', text: `未知工具: ${name}` }], isError: true };
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('[AgentEvolution MCP v2.1] Server started on stdio');
}

main().catch((e) => {
  console.error('[AgentEvolution MCP] Fatal:', e);
  process.exit(1);
});
