#!/bin/bash
# GitHub 仓库 About 和 Topics 更新脚本

set -e

REPO="yadinae/agent-evolution"

echo "🔄 更新 GitHub 仓库配置..."

# 检查 gh 是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI 未安装，请先安装：sudo apt install gh 或 brew install gh"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "❌ 未登录 GitHub，请先登录：gh auth login"
    exit 1
fi

# 更新仓库描述
echo "📝 更新仓库描述..."
gh repo edit "$REPO" \
  --description "🧬 Agent 自我进化系统 - 基于数据驱动的 AI Agent 能力提升平台 | ✨ 任务监控/技能评估/智能调度/自动进化 | 📊 95%+ 测试覆盖，<20ms 延迟"

# 添加 Topics
echo "🏷️  添加 Topics..."
TOPICS=(
  "ai-agent"
  "self-improvement"
  "machine-learning"
  "automation"
  "performance-monitoring"
  "skill-evaluation"
  "intelligent-scheduling"
  "data-driven"
  "python"
  "open-source"
  "agent-evolution"
  "ai-optimization"
)

for topic in "${TOPICS[@]}"; do
  echo "  添加：$topic"
  gh repo edit "$REPO" --add-topic "$topic"
done

echo ""
echo "✅ GitHub 仓库配置更新完成！"
echo ""
echo "📋 仓库地址：https://github.com/$REPO"
echo "🏷️  Topics: ${TOPICS[*]}"
echo ""
