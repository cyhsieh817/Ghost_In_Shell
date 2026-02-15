# 22_mem0_Integration: 本地向量記憶系統

> **將 mem0 + Qdrant + Ollama 整合為語意加速層。**

---

## 為什麼需要 mem0？

Vault 是人類可讀的長期記憶，但 AI 需要**語意搜尋**能力：
- 搜尋「偏好的設定」→ 找到所有相關記憶
- 對話要點摘要 → 快速回顧上下文
- 語意相似匹配 → 非關鍵字搜尋

---

## 系統架構

```
輸入 → Vault (長期)
       ↓
可選 → mem0 (加速)

查詢 → Vault (首選)
       ↓ 無結果
       mem0 (輔助)
```

---

## 前置需求

| 組件 | 用途 | 狀態 |
|------|------|------|
| Qdrant | 向量資料庫 | Docker 運行中 |
| Ollama | 本地 LLM + Embedding | 運行中 |
| mem0ai | Python 套件 | pip install mem0ai |

---

## 安裝步驟

### 1. 啟動 Qdrant

```bash
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
```

### 2. 啟動 Ollama

```bash
ollama serve
# 確保有以下模型：
ollama pull llama3.2:latest
ollama pull nomic-embed-text
```

### 3. 安裝 mem0ai

```bash
pip3 install mem0ai
```

---

## 技能設定 (OpenClaw Skill)

### 目錄結構

```
~/.openclaw/skills/mem0/
├── skill.py    # 核心程式
├── cmd.sh      # 快速指令
└── SKILL.md    # 說明文件
```

### skill.py 範例

```python
import os
os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

from mem0 import Memory

config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "agent_memory",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 768
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2:latest",
            "ollama_base_url": "http://localhost:11434"
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434"
        }
    }
}

client = Memory.from_config(config)

# 新增記憶
client.add("吾主偏好簡潔回覆", user_id="my_lord")

# 搜尋
client.search(query="偏好", user_id="my_lord")

# 列出
client.get_all(user_id="my_lord")
```

---

## 使用方式

### 快速指令

```bash
# 新增記憶
mem0 add "吾主偏好簡潔回覆" --user my_lord

# 搜尋記憶
mem0 search "偏好" --user my_lord

# 列出所有記憶
mem0 list --user my_lord
```

### 自動化

在 Agent 對話結束後自動記錄要點：

```
對話結束 → 提取要點 → mem0 add
```

---

## 與 Vault 的協作

| 時機 | 動作 |
|------|------|
| 汝告知偏好 | mem0 add (加速) |
| 完成重要任務 | 寫入 Vault (長期) |
| 需要快速回憶 | mem0 search |

---

## 注意事項

1. **Vault 優先**：mem0 是加速層，非必要
2. **人類不可讀**：向量庫內容無法直接閱讀
3. **可重建**：異常時從 Vault 重建即可

---

> **下一步**：想看完整的實戰案例？[21_Real_World_Example](21_Real_World_Example.md)

> 返回 [總覽](00_Overview.md)
