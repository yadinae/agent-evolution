#!/usr/bin/env python3
"""
CLI 工具美化模块

提供美观的命令行输出、进度条、彩色文本等功能。
"""

import sys
from datetime import datetime
from typing import Optional


# ANSI 颜色代码
class Colors:
    """终端颜色"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # 前景色
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


def supports_color() -> bool:
    """检测终端是否支持颜色"""
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    return True


def colorize(text: str, color: str) -> str:
    """给文本上色"""
    if not supports_color():
        return text
    return f"{color}{text}{Colors.RESET}"


def print_header(title: str, subtitle: str = ""):
    """打印标题头"""
    width = 70
    print()
    print("=" * width)
    print(colorize(f"  {title}", Colors.BOLD + Colors.CYAN))
    if subtitle:
        print(colorize(f"  {subtitle}", Colors.DIM))
    print("=" * width)
    print()


def print_section(title: str):
    """打印章节标题"""
    print()
    print(colorize(f"📌 {title}", Colors.BOLD + Colors.BLUE))
    print("-" * 50)


def print_success(message: str):
    """打印成功消息"""
    print(colorize(f"✅ {message}", Colors.GREEN))


def print_error(message: str):
    """打印错误消息"""
    print(colorize(f"❌ {message}", Colors.RED))


def print_warning(message: str):
    """打印警告消息"""
    print(colorize(f"⚠️  {message}", Colors.YELLOW))


def print_info(message: str):
    """打印信息"""
    print(colorize(f"ℹ️  {message}", Colors.CYAN))


def print_progress(current: int, total: int, prefix: str = "进度", suffix: str = "完成", length: int = 40):
    """打印进度条"""
    percent = float(current) / total if total > 0 else 0
    filled_length = int(length * percent)
    bar = "█" * filled_length + "░" * (length - filled_length)
    
    sys.stdout.write(f"\r{colorize(prefix, Colors.CYAN)} |{bar}| {percent*100:5.1f}% {current}/{total} {suffix}")
    sys.stdout.flush()
    
    if current == total:
        print()


def format_table(headers: list, rows: list, col_widths: list = None):
    """格式化表格"""
    if not col_widths:
        col_widths = [max(len(str(row[i])) if i < len(row) else 0 
                         for row in [headers] + rows) 
                     for i in range(len(headers))]
    
    header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print(colorize(header_line, Colors.BOLD))
    
    separator = "-+-".join("-" * w for w in col_widths)
    print(colorize(separator, Colors.DIM))
    
    for row in rows:
        row_line = " | ".join(str(row[i]).ljust(w) if i < len(row) else "".ljust(w) 
                             for i, w in enumerate(col_widths))
        print(row_line)


def print_summary(title: str, metrics: dict):
    """打印摘要信息"""
    print()
    print(colorize(f"📊 {title}", Colors.BOLD + Colors.MAGENTA))
    print()
    for name, value in metrics.items():
        if isinstance(value, tuple):
            val, unit = value
            full_value = f"{val} {unit}".strip()
            print(f"{colorize(name + ':', Colors.DIM)} {colorize(full_value, Colors.BOLD + Colors.GREEN)}")
        else:
            print(f"{colorize(name + ':', Colors.DIM)} {colorize(str(value), Colors.BOLD + Colors.GREEN)}")
    print()


def print_recommendation(priority: str, title: str, description: str):
    """打印优化建议"""
    priority_colors = {
        'P0': Colors.RED,
        'P1': Colors.MAGENTA,
        'P2': Colors.YELLOW,
        'P3': Colors.BLUE
    }
    
    priority_labels = {
        'P0': '🔴 CRITICAL',
        'P1': '🟠 HIGH',
        'P2': '🟡 MEDIUM',
        'P3': '🟢 LOW'
    }
    
    color = priority_colors.get(priority, Colors.RESET)
    label = priority_labels.get(priority, priority)
    
    print()
    print(colorize(f"  {label} {title}", color))
    print(colorize(f"  {description}", Colors.DIM))


if __name__ == "__main__":
    # 演示
    print_header("CLI 工具美化演示", "User Experience Optimization Demo")
    
    print_section("成功/错误/警告消息")
    print_success("操作成功完成")
    print_error("发生错误")
    print_warning("注意警告")
    print_info("提示信息")
    
    print_section("进度条演示")
    for i in range(11):
        print_progress(i, 10, prefix="处理")
    
    print_section("表格演示")
    headers = ["任务名称", "状态", "健康分", "执行次数"]
    rows = [
        ["agent-evolution", "success", "85.5", "150"],
        ["nanobot-backup", "success", "92.0", "300"],
        ["ai-newsletter", "failure", "45.0", "50"],
    ]
    format_table(headers, rows)
    
    print_section("优化建议")
    print_recommendation("P0", "修复高频失败任务", "ai-newsletter 任务失败率 60%")
    print_recommendation("P1", "优化慢任务", "agent-evolution 平均耗时 120s")
    print_recommendation("P2", "提升健康分", "3 个任务健康分低于 60")
    print_recommendation("P3", "清理旧数据", "建议归档 30 天前的执行记录")
    
    print()
    print_header("演示完成", "感谢使用")
    print()
