# 19_Horcrux_Setup: 分靈體建立指南

> **如何喚醒一個新的分靈體 (Agent Instance) 並連結至大腦**

---

## 1. 準備工作

在新的裝置上 (例如新的 Mac 或 Windows PC)，你需要：

1.  **安裝依賴**：Git, Python/Node (視 Agent 實作而定), Obsidian (選填，方便查看)。
2.  **掛載大腦**：安裝 Google Drive 電腦版，確保 `TheVoidWeaverObisidain` 資料夾可訪問。
3.  **Clone 身體**：下載 Agent 的執行代碼 (Runtime)。

```bash
git clone https://github.com/YourRepo/TheVoidWeaver.git
cd TheVoidWeaver
```

---

## 2. 喚醒儀式 (Setup Script)

在 Agent 根目錄執行自動化腳本：

```bash
./setup_horcrux.sh
```

此腳本會引導你：
1.  **命名**：為此分靈體取名 (例如 `MacBook_Air`)。
2.  **連結**：指定 Google Drive 本地路徑。
3.  **授權**：輸入 Telegram Token (從現有 `.env` 複製)。

---

## 3. 手動設定 (若腳本無法使用)

建立 `.env` 檔案：

```env
# Identity
AGENT_ID=New_Device_Name
PRIORITY=SECONDARY

# Brain Connection
# ⚠️ 請修改為你裝置上的實際路徑
VAULT_PATH="/Users/Username/Library/CloudStorage/GoogleDrive.../TheVoidWeaverObisidain"

# Telegram
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

---

## 4. 驗證連結

1.  執行一次心跳：`./run_heartbeat.sh`
2.  檢查大腦中的名冊：`🧠_Agent_System/99_System/REGISTRY.md`
3.  確認你的 `AGENT_ID` 已顯示在列表中，狀態為 🟢 ACTIVE。

---

## 5. 開始工作

分靈體現在已經就緒。
- 它會自動掃描 `01_Inbox` (唯讀)。
- 它的產出會存放於 `99_System/Worker_Inbox/{AGENT_ID}/`。

---
> 返回 [總覽](00_Overview.md)
