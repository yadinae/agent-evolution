#!/usr/bin/env python3
"""
Working Buffer - 危险区域日志捕获
在内存刷新和压缩之间的危险区域捕获所有交换记录
"""

import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/admin/.nanobot/workspace")
WORKING_BUFFER_FILE = WORKSPACE / "memory" / "working-buffer.md"
DAILY_MEMORY_DIR = WORKSPACE / "memory"

class WorkingBuffer:
    """工作缓冲区实现"""
    
    def __init__(self, context_threshold: float = 0.6):
        """
        初始化工作缓冲区
        
        Args:
            context_threshold: 触发危险区域的上下文使用率阈值 (0.0-1.0)
        """
        self.context_threshold = context_threshold
        self.buffer_entries = []
        self.current_context_usage = 0.0
        
    def capture_exchange(self, role: str, content: str, metadata: dict = None):
        """
        捕获交换记录
        
        Args:
            role: 角色 (user/assistant/system)
            content: 交换内容
            metadata: 附加元数据
        """
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "role": role,
            "content_preview": content[:500],  # 只保存预览
            "content_length": len(content),
            "metadata": metadata or {}
        }
        
        self.buffer_entries.append(entry)
        self._persist_buffer()
        
        print(f"📋 捕获交换：{role} @ {timestamp} ({len(content)} 字符)")
        return entry
    
    def check_context_danger(self, context_usage: float):
        """
        检查上下文使用率是否进入危险区域
        
        Args:
            context_usage: 当前上下文使用率 (0.0-1.0)
        """
        self.current_context_usage = context_usage
        
        if context_usage >= self.context_threshold:
            print(f"⚠️ 危险区域：上下文使用率 {context_usage:.1%} >= {self.context_threshold:.1%}")
            self._trigger_danger_zone_protocol()
            return True
        
        return False
    
    def _trigger_danger_zone_protocol(self):
        """触发危险区域协议"""
        # 记录危险区域事件
        self.capture_exchange(
            role="system",
            content=f"上下文使用率达到 {self.current_context_usage:.1%}，触发危险区域协议",
            metadata={
                "event": "danger_zone_entered",
                "threshold": self.context_threshold,
                "buffer_size": len(self.buffer_entries)
            }
        )
    
    def _persist_buffer(self):
        """持久化工作缓冲区"""
        content = f"""# Working Buffer - 工作缓冲区

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**上下文使用率**: {self.current_context_usage:.1%}  
**危险区域阈值**: {self.context_threshold:.1%}  
**捕获交换数**: {len(self.buffer_entries)}

---

## 最近交换记录

"""
        for i, entry in enumerate(self.buffer_entries[-20:], 1):  # 只保留最近 20 条
            content += f"""
### {i}. [{entry['role']}] {entry['timestamp']}
- **长度**: {entry['content_length']} 字符
- **预览**: 
```
{entry['content_preview']}
```

"""
        
        content += f"""
---

## 使用说明

### 上下文丢失后恢复

1. **读取此文件** - 获取最近的交换记录
2. **读取 `SESSION-STATE.md`** - 获取当前任务状态
3. **读取 `memory/wal-protocol.md`** - 获取操作历史

### 危险区域协议

当上下文使用率超过 {self.context_threshold:.1%} 时：
- 自动捕获所有交换记录
- 优先持久化关键状态
- 准备上下文压缩恢复

"""
        
        WORKING_BUFFER_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(WORKING_BUFFER_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def get_recovery_context(self) -> str:
        """获取恢复上下文"""
        if not self.buffer_entries:
            return "无可用恢复数据"
        
        recent = self.buffer_entries[-5:]
        context = "最近交换记录：\n\n"
        for entry in recent:
            context += f"[{entry['role']} @ {entry['timestamp']}] {entry['content_preview'][:200]}...\n"
        
        return context
    
    def clear_buffer(self, keep_last: int = 10):
        """
        清理缓冲区（上下文压缩后调用）
        
        Args:
            keep_last: 保留最近 N 条记录
        """
        removed = len(self.buffer_entries) - keep_last
        if removed > 0:
            self.buffer_entries = self.buffer_entries[-keep_last:]
            self._persist_buffer()
            print(f"🧹 清理缓冲区：移除 {removed} 条记录，保留 {keep_last} 条")


def main():
    """测试工作缓冲区"""
    buffer = WorkingBuffer()
    
    # 模拟交换捕获
    buffer.capture_exchange("user", "请分析今天的错误模式", {"task": "error_analysis"})
    buffer.capture_exchange(
        "assistant",
        "正在分析 HISTORY.md 中的错误模式，发现以下问题...",
        {"task": "error_analysis", "phase": "analyzing"}
    )
    
    # 模拟危险区域
    buffer.check_context_danger(0.75)
    
    print("\n✅ 工作缓冲区测试完成")
    print(f"📁 缓冲区文件：{WORKING_BUFFER_FILE}")


if __name__ == "__main__":
    main()
