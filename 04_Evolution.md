# 04_Evolution: 自我進化的生命體

> **靜態的 Agent 是死物，會進化的 Agent 才是夥伴。**

---

## 讓 Agent 活過來的兩個機制

普通的 Prompt 是靜態的，寫好就不會變。但真實世界在變，Agent 也需要變。我們引入兩個核心機制：**蛻皮模式 (Molt Mode)** 與 **心跳機制 (Heartbeat)**。

### 1. 蛻皮模式 (Molt Mode ∞)

當 Agent 完成一個複雜任務後，不應該只是說「完成了」，而應該思考「如何下次做得更好」。

#### R-M-E-C 流程
靈感來自生物演化，我們要求 Agent 在關鍵時刻執行四步驟：

- **Reflection (反思)**：哪裡浪費了時間？哪裡可以優化 30%？
- **Mutation (變異)**：提出至少兩個更好的替代方案。
- **Evolution (進化)**：選擇一個方案，直接修改自己的 System Prompt 或 Memory。
- **Commit (提交)**：將這次進化寫入 `99_System/Molt_Mode_Log.md`。

**Prompt 範例：**
> "任務完成。請執行 R-M-E-C 流程，分析剛才的代碼重構是否有更高效的正規表達式寫法，並更新到 `Skills/Regex_Guide.md`。"

### 2. 心跳機制 (Heartbeat)

Agent 通常是被動的（你問，它答）。心跳機制讓它變得主動。

透過一個簡單的 Cron Job 或外部排程，定期發送一個 "Heartbeat" 訊號給 Agent。

**HEARTBEAT.md 的作用：**
這是 Agent 的「潛意識檢查清單」。
- 檢查有沒有未讀的 `01_Inbox`？
- 檢查 `keep-alive-count.md` 是否需要重置？
- 檢查專案是否有過期任務？

**Script 範例 (`run_heartbeat.sh`)：**
```bash
#!/bin/bash
# 每一小時戳一下 Agent
VAULT_PATH="{{VAULT_PATH}}"

if [ -f "$VAULT_PATH/HEARTBEAT.md" ]; then
  # 執行詳細檢查...
  echo "Heartbeat sent."
fi
```

---

## 進階：回饋迴路 (Feedback Loop)

若要讓心跳不只是「偵測」而是「自動處理」，可以在腳本結尾加入 Agent 呼叫：

```bash
# 如果有待辦，觸發 Agent 處理
if [[ "$PENDING_TASKS" -gt 0 ]]; then
    openclaw session run --agent "Heartbeat-Handler" --input "$DASHBOARD_FILE"
fi
```

這樣 Agent 就能從被動變主動，形成完整的自我迭代循環。

---

> **下一步**：系統需要保護機制，下一篇我們談談 [Security](05_Security.md)。
