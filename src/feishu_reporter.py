#!/usr/bin/env python3
"""
Feishu Reporter - 飞书主动报告机制 (修复版)
修复 agent-evolution 的主动通知功能
"""

import os
import json
import re
import requests
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

WORKSPACE = Path("/home/admin/.nanobot/workspace")
CONFIG_FILE = WORKSPACE.parent / "config.json"

class FeishuReporter:
    """飞书报告器"""
    
    def __init__(self):
        self.config = self._load_config()
        self.tenant_access_token = None
        
        # 从 .env 读取配置（优先）
        self.app_id = os.getenv('FEISHU_APP_ID')
        self.app_secret = os.getenv('FEISHU_APP_SECRET')
        self.channel_id = os.getenv('FEISHU_CHANNEL_ID', 'ou_608260b868adf690d70569214d83cfda')
        
        # 如果 .env 没有，从 config.json 读取
        if not self.app_id or not self.app_secret:
            feishu_config = self.config.get('channels', {}).get('feishu', {})
            self.app_id = feishu_config.get('appId') or feishu_config.get('app_id')
            self.app_secret = feishu_config.get('appSecret') or feishu_config.get('app_secret')
        
        if not self.channel_id:
            feishu_config = self.config.get('channels', {}).get('feishu', {})
            self.channel_id = feishu_config.get('channelId') or feishu_config.get('channel_id')
        
        self._load_config()
        
    def _load_config(self) -> dict:
        """加载配置"""
        if not CONFIG_FILE.exists():
            return {}
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_tenant_access_token(self) -> str:
        """获取飞书 tenant_access_token"""
        if self.tenant_access_token:
            return self.tenant_access_token
        
        if not self.app_id or not self.app_secret:
            raise ValueError("飞书 App ID 或 Secret 未配置（检查 .env 或 config.json）")
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get('code') != 0:
            raise Exception(f"获取 token 失败：{result.get('msg')}")
        
        self.tenant_access_token = result['tenant_access_token']
        return self.tenant_access_token
    
    def send_evolution_report(self, report_path: str, channel_id: str = None, force_send: bool = False):
        """
        发送进化报告到飞书
        
        Args:
            report_path: 进化报告文件路径
            channel_id: 飞书频道 ID（默认使用配置中的频道）
            force_send: 强制发送（忽略静默模式）
        """
        # 检查静默模式偏好
        if not force_send and self._is_silent_mode():
            print("ℹ️  静默模式已启用 - 跳过飞书通知（无异常）")
            return {"status": "skipped", "reason": "silent_mode"}
        
        if not Path(report_path).exists():
            raise FileNotFoundError(f"报告文件不存在：{report_path}")
        
        # 读取报告内容
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        
        # 确定目标频道
        target_channel = channel_id or self.channel_id
        
        if not target_channel:
            raise ValueError("飞书频道 ID 未配置")
        
        # 转换为飞书消息格式
        message = self._markdown_to_feishu_message(report_content)
        
        # 发送消息
        return self._send_text_message(target_channel, message)
    
    def _is_silent_mode(self) -> bool:
        """
        检查是否启用了静默模式
        读取 HEARTBEAT.md 中的用户偏好
        """
        heartbeat_file = WORKSPACE / "memory" / "HEARTBEAT.md"
        if not heartbeat_file.exists():
            return False
        
        with open(heartbeat_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含静默模式配置
        silent_keywords = [
            "飞书通知策略",
            "无异常时不发送飞书消息",
            "只在有异常或重要事件时才发送通知",
            "静默模式"
        ]
        
        has_silent_config = any(keyword in content for keyword in silent_keywords)
        
        if not has_silent_config:
            return False
        
        # 只检查 Pending Tasks 章节是否有异常（而不是 Completed Tasks）
        # 因为 Completed Tasks 中的"错误"等词是历史记录，不是当前异常
        pending_tasks_section = ""
        if "## Pending Tasks" in content:
            pending_start = content.index("## Pending Tasks")
            if "## Completed Tasks" in content:
                pending_end = content.index("## Completed Tasks", pending_start)
                pending_tasks_section = content[pending_start:pending_end]
            else:
                pending_tasks_section = content[pending_start:]
        
        # 检查 Pending Tasks 中是否包含异常/重要事件
        anomaly_keywords = [
            "异常",
            "错误",
            "失败",
            "告警",
            "重要事件",
            "P0",
            "严重"
        ]
        
        has_anomaly_in_pending = any(keyword in pending_tasks_section for keyword in anomaly_keywords)
        
        # 静默模式启用且 Pending Tasks 中无异常 → 不发送通知
        if not has_anomaly_in_pending:
            return True
        
        return False
    
    def check_report_for_anomalies(self, report_path: str) -> bool:
        """
        检查进化报告中是否包含异常或重要事件
        
        Args:
            report_path: 进化报告文件路径
            
        Returns:
            bool: True 表示有异常需要发送通知
        """
        if not Path(report_path).exists():
            return False
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键指标
        anomaly_indicators = [
            # 错误数量超过阈值
            r'错误.*1000|Error.*1000',
            # 严重错误
            r'严重|Critical|Fatal',
            # P0 优先级
            r'P0|优先级.*0|最高优先级',
            # 系统问题
            r'系统崩溃|System Crash|数据丢失|Data Loss',
            # API 问题
            r'API 配额耗尽|Quota Exhausted|认证失败',
        ]
        
        # 检查是否有异常指标
        has_anomaly = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in anomaly_indicators
        )
        
        return has_anomaly
    
    def _send_text_message(self, channel_id: str, message: str) -> dict:
        """
        发送文本消息到飞书
        
        Args:
            channel_id: 接收者 ID
            message: 消息内容
        """
        token = self.get_tenant_access_token()
        # receive_id_type 必须放在 URL 查询参数中
        url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 请求体中不需要 receive_id_type
        payload = {
            "receive_id": channel_id,
            "msg_type": "text",
            "content": json.dumps({"text": message}, ensure_ascii=False)
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        
        if result.get('code') != 0:
            error_msg = result.get('msg', '未知错误')
            print(f"❌ API 响应：{json.dumps(result, ensure_ascii=False, indent=2)}")
            raise Exception(f"发送消息失败：{error_msg}")
        
        message_id = result.get('data', {}).get('message_id')
        print(f"✅ 飞书消息已发送：{message_id}")
        
        return {
            "status": "success",
            "message_id": message_id,
            "channel_id": channel_id
        }
    
    def _markdown_to_feishu_message(self, markdown: str) -> str:
        """
        将 Markdown 转换为飞书消息文本
        
        飞书支持部分 Markdown 语法：
        - **加粗**
        - *斜体*
        - [链接](url)
        - `行内代码`
        - 引用块
        """
        # 简化处理：提取关键信息
        lines = markdown.split('\n')
        message_lines = []
        
        for line in lines[:50]:  # 限制长度
            if line.startswith('# '):
                message_lines.append(f"**{line[2:]}**")
            elif line.startswith('## '):
                message_lines.append(f"\n**{line[3:]}**")
            elif line.startswith('- '):
                message_lines.append(f"• {line[2:]}")
            elif line.startswith('**'):
                message_lines.append(line)
            elif line.strip():
                message_lines.append(line)
        
        # 添加摘要
        summary = f"\n\n📊 Agent 进化报告已完成\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return '\n'.join(message_lines[:30]) + summary
    
    def send_notification(self, title: str, content: str, channel_id: str = None):
        """
        发送简单通知
        
        Args:
            title: 通知标题
            content: 通知内容
            channel_id: 飞书频道 ID
        """
        target_channel = channel_id or self.channel_id
        
        if not target_channel:
            raise ValueError("飞书频道 ID 未配置")
        
        message = f"**{title}**\n\n{content}"
        
        return self._send_text_message(target_channel, message)


def main():
    """测试飞书报告机制"""
    reporter = FeishuReporter()
    
    # 测试发送通知
    try:
        result = reporter.send_notification(
            title="🧬 Agent Evolution v2.0 测试",
            content="WAL 协议、Working Buffer、飞书报告机制已整合完成，等待 Heartbeat 任务验证",
            channel_id="ou_608260b868adf690d70569214d83cfda"
        )
        print(f"✅ 测试成功：{result}")
    except Exception as e:
        print(f"❌ 测试失败：{e}")


if __name__ == "__main__":
    main()
