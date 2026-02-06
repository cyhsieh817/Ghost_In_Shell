# 09_Multi_Agent_Sync: 多重分靈體架構 (Horcrux Architecture)

> **多裝置、多實例、單一大腦、零衝突**

---

## 核心哲學：分靈體系統

我們採用 **混合式架構 (Hybrid Architecture)** 來實現無限擴展：

1. **共享大腦 (Shared Brain)**：Google Drive 是唯一的真理。
2. **分區寫入 (Partitioned Write)**：每個分靈體 (Horcrux) 只能寫入自己的專屬收件匣。
3. **中央協調 (Telegram Hub)**：重大決策透過 Telegram 匯流排通知。

---

## 📂 檔案結構

```
🧠_Agent_System/
└── 99_System/
    ├── REGISTRY.md           # 分靈體名冊
    ├── ACTIVE_LOCKS/         # 核心操作鎖 (僅限 LOCKED 任務)
    └── Worker_Inbox/         # 分區輸出 (零衝突關鍵)
        ├── MacBook_Pro/      # 分靈體 A 專用
        ├── Win_Desktop/      # 分靈體 B 專用
        └── ...
```

---

## 🔄 同步協議

### 1. 讀取 (READ)
所有分靈體都有權**讀取**整個 `🧠_Agent_System` 與 `📂_User_Workspace`。
這確保了知識共享。

### 2. 寫入 (WRITE) - 平行作業
一般任務（AUTO/CONFIRM/PROPOSE）：
- **只能寫入**：`99_Sync_Hub/Worker_Inbox/{AGENT_ID}/`
- **範例**：分靈體 A 完成了一份報告，它會將報告存為 `Worker_Inbox/A/報告_v1.md`，然後發送 Telegram 通知人類查閱。

### 3. 寫入 (WRITE) - 核心操作
核心任務（LOCKED，如修改 `MEMORY.md`）：
- 必須先搶佔 `LOCKS/{TargetFile}.lock`。
- 搶鎖成功 -> 執行修改 -> 釋放鎖。
- 搶鎖失敗 -> 等待或放棄。

---

## 🤖 分靈體身份識別

每個執行環境 (Runtime) 必須擁有一個 `.env` 檔案：

```env
# 分靈體身分證
AGENT_ID=MacBook_Pro    # 唯一 ID
PRIORITY=PRIMARY        # 衝突時優先級 (PRIMARY/SECONDARY)

# 大腦連結
VAULT_PATH=/path/to/GoogleDrive/TheVoidWeaverObisidain

# 協調中心
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

---

## 🚀 如何新增分靈體？

請參閱 [19_Horcrux_Setup](19_Horcrux_Setup.md) 安裝指南。

---
> 返回 [總覽](00_Overview.md)
