#!/usr/bin/env python3
"""
WAL Protocol - Write-Ahead Logging for Agent Evolution
确保在上下文丢失前记录关键状态，支持恢复
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/admin/.nanobot/workspace")
WAL_FILE = WORKSPACE / "memory" / "wal-protocol.md"
SESSION_STATE_FILE = WORKSPACE / "SESSION-STATE.md"

class WALProtocol:
    """WAL 协议实现"""
    
    def __init__(self):
        self.wal_entries = []
        self.session_state = {}
        
    def log_entry(self, entry_type: str, data: dict, before_action: bool = True):
        """
        记录 WAL 条目
        
        Args:
            entry_type: 条目类型 (evolution_start, learning, optimization, etc.)
            data: 条目数据
            before_action: 是否在动作之前记录 (true=WAL 模式)
        """
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "type": entry_type,
            "before_action": before_action,
            "data": data
        }
        
        self.wal_entries.append(entry)
        self._persist_wal()
        
        print(f"📝 WAL 记录：{entry_type} @ {timestamp}")
        return entry
    
    def _persist_wal(self):
        """持久化 WAL 日志"""
        content = f"""# WAL Protocol Log - 写前日志

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**条目数量**: {len(self.wal_entries)}

---

## 日志条目

"""
        for i, entry in enumerate(self.wal_entries[-50:], 1):  # 只保留最近 50 条
            content += f"""
### {i}. [{entry['type']}] {entry['timestamp']}
- **Before Action**: {entry['before_action']}
- **Data**: {json.dumps(entry['data'], ensure_ascii=False, indent=2)}

"""
        
        WAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(WAL_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def update_session_state(self, state: dict):
        """更新会话状态"""
        self.session_state.update(state)
        self._persist_session_state()
        
    def _persist_session_state(self):
        """持久化会话状态"""
        content = f"""# Session State - 活跃会话状态

**最后更新**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**WAL 条目数**: {len(self.wal_entries)}

---

## 当前状态

{json.dumps(self.session_state, ensure_ascii=False, indent=2)}

---

## 恢复指南

如果上下文丢失：
1. 读取此文件获取当前任务状态
2. 读取 `memory/wal-protocol.md` 获取最近操作历史
3. 从最后一个 `before_action: true` 的条目恢复

"""
        
        with open(SESSION_STATE_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def recover_from_compaction(self):
        """从上下文压缩中恢复"""
        if not WAL_FILE.exists():
            return {"status": "error", "message": "WAL 文件不存在"}
        
        # 读取最近的 WAL 条目
        recent_entries = self.wal_entries[-10:] if self.wal_entries else []
        
        return {
            "status": "success",
            "recent_entries": recent_entries,
            "session_state": self.session_state,
            "recovery_hint": f"从 {len(recent_entries)} 个 WAL 条目恢复"
        }


def main():
    """测试 WAL 协议"""
    wal = WALProtocol()
    
    # 模拟进化流程
    wal.log_entry("evolution_start", {
        "trigger": "heartbeat",
        "source_files": ["MEMORY.md", "HISTORY.md"]
    })
    
    wal.update_session_state({
        "current_task": "agent_evolution",
        "phase": "analyzing",
        "started_at": datetime.now().isoformat()
    })
    
    print("✅ WAL 协议测试完成")
    print(f"📁 WAL 文件：{WAL_FILE}")
    print(f"📁 会话状态：{SESSION_STATE_FILE}")


if __name__ == "__main__":
    main()
