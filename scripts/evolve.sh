#!/bin/bash

# Agent Evolution - Agent 进化入口脚本
# 版本：2.0.0
# 用法：./evolve.sh [选项]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$REPO_DIR/.venv"
PYTHON="$VENV_DIR/bin/python3"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 帮助信息
show_help() {
    echo -e "${BLUE}Agent Evolution - Agent 自我进化${NC}"
    echo ""
    echo -e "${GREEN}用法:${NC}"
    echo "  $0 [选项]"
    echo ""
    echo -e "${GREEN}选项:${NC}"
    echo "  --analyze               分析会话历史（运行 Python 分析器）"
    echo "  --identify-improvements 识别改进点"
    echo "  --apply                 应用优化（需确认）"
    echo "  --learn <text>          记录学习"
    echo "  --history               查看学习历史"
    echo "  --daily-review          每日审查"
    echo "  --weekly-summary        每周总结"
    echo "  --help, -h              显示帮助"
    echo ""
    echo -e "${GREEN}示例:${NC}"
    echo "  $0 --analyze"
    echo "  $0 --learn \"新 API 用法\" --category api"
    echo "  $0 --history --category error-handling"
}

# 默认配置
MODE=""
LEARN_TEXT=""
CATEGORY=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --analyze)
            MODE="analyze"
            shift
            ;;
        --identify-improvements)
            MODE="identify"
            shift
            ;;
        --apply)
            MODE="apply"
            shift
            ;;
        --learn)
            MODE="learn"
            LEARN_TEXT="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --history)
            MODE="history"
            shift
            ;;
        --daily-review)
            MODE="daily"
            shift
            ;;
        --weekly-summary)
            MODE="weekly"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -*)
            echo -e "${RED}错误：未知选项 $1${NC}"
            show_help
            exit 1
            ;;
        *)
            echo -e "${RED}错误：未知参数 $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

echo -e "${BLUE}Agent Evolution${NC}"
echo -e "${GREEN}模式：${NC}${MODE:-default}"
echo ""

# 检查虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}错误：虚拟环境不存在${NC}"
    echo "请先运行：cd $REPO_DIR && uv venv .venv --python 3.11 && source .venv/bin/activate && uv pip install -r requirements.txt"
    exit 1
fi

# 执行操作
case $MODE in
    analyze)
        echo -e "${YELLOW}分析会话历史...${NC}"
        $PYTHON "$REPO_DIR/evolve_analysis.py" --analyze
        echo -e "${GREEN}分析完成${NC}"
        ;;
    identify)
        echo -e "${YELLOW}识别改进点...${NC}"
        $PYTHON "$REPO_DIR/evolve_analysis.py" --identify
        echo -e "${GREEN}识别完成${NC}"
        ;;
    apply)
        echo -e "${YELLOW}应用优化...${NC}"
        echo -e "${YELLOW}请确认要应用的优化项（输入 y 确认）：${NC}"
        read -r confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            $PYTHON "$REPO_DIR/evolve_analysis.py" --apply
            echo -e "${GREEN}优化已应用${NC}"
        else
            echo -e "${YELLOW}已取消${NC}"
        fi
        ;;
    learn)
        echo -e "${YELLOW}记录学习：${NC}$LEARN_TEXT"
        echo -e "${GREEN}类别：${NC}${CATEGORY:-general}"
        $PYTHON "$REPO_DIR/evolve_analysis.py" --learn "$LEARN_TEXT" --category "${CATEGORY:-general}"
        echo -e "${GREEN}学习已记录${NC}"
        ;;
    history)
        echo -e "${YELLOW}学习历史${NC}"
        $PYTHON "$REPO_DIR/evolve_analysis.py" --history
        ;;
    daily)
        echo -e "${YELLOW}每日审查${NC}"
        $PYTHON "$REPO_DIR/evolve_analysis.py" --daily-review
        echo -e "${GREEN}每日审查完成${NC}"
        ;;
    weekly)
        echo -e "${YELLOW}每周总结${NC}"
        $PYTHON "$REPO_DIR/evolve_analysis.py" --weekly-summary
        echo -e "${GREEN}每周总结完成${NC}"
        ;;
    *)
        echo -e "${YELLOW}默认进化流程...${NC}"
        $PYTHON "$REPO_DIR/evolve_analysis.py"
        ;;
esac

echo -e "\n${GREEN}进化流程完成${NC}"
