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

> **💡 Note**: 若此分靈體已存在，腳本會自動偵測並詢問是否覆蓋設定檔。選擇 `n` (預設) 即可在保留記憶的情況下修復/更新核心架構。

---

## 3. 手動設定 (若腳本無法使用)

若無法執行 `setup_horcrux.sh`，請依照以下步驟手動建立設定：

1.  **複製模板**：
    開啟 `🧠_Agent_System/00_Self_Introduction/_TEMPLATE_ENV.md`，將內容複製並存為 `.env` (位於 Agent 根目錄)。

2.  **填寫關鍵變數**：
    *   **本體 (Main Body)**：
        ```bash
        OBSIDIAN_VAULT_PATH="/Users/cyuh/Documents/MyAITeam/TheViodWeaver"
        PRIORITY="PRIMARY"
        ```
    *   **分靈體 (Clone/Backup)**：
        ```bash
        OBSIDIAN_VAULT_PATH="/Users/cyuh/Library/CloudStorage/GoogleDrive-cyhsieh@yc-biotech.net/My Drive/TheVoidWeaverObisidain"
        PRIORITY="SECONDARY"
        ```

3.  **其他設定**：
    *   `AGENT_ID`：為此裝置取名 (如 `MacBook_Pro`)。
    *   `TELEGRAM_BOT_TOKEN` / `CHAT_ID`：填入以啟用通知。

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

## 6. 腳本還原與維護 (Script Maintenance)

所有核心執行腳本皆有 Markdown 備份，若腳本遺失或損壞，可從備份還原：

| 腳本 | 備份位置 (於 `00_Self_Introduction/`) | 用途 |
| :--- | :--- | :--- |
| `run_heartbeat.sh` | `_BACKUP_run_heartbeat.md` | 核心心跳與監控 |
| `git_backup.sh` | `_BACKUP_git_backup.md` | Git 自動同步 |
| `setup_horcrux.sh` | `_BACKUP_setup_horcrux.md` | 初始化設定 |

**還原步驟**：
1. 開啟對應的 `_BACKUP_*.md` 檔案。
2. 複製代碼區塊 (Code Block) 的內容。
3. 貼上至同名 `.sh` 檔案。
4. 賦予執行權限：`chmod +x filename.sh`

---

## 7. OpenClaw 整合（選填）

若使用 OpenClaw 作為 Agent 引擎，建立分靈體後還需：

1. **建立 Agent 目錄**：`mkdir -p ~/.openclaw/agents/{{AGENT_NAME}}/agent`
2. **設定工作區**：在 `openclaw.json` 的 `agents` 區塊指向分靈體工作區
3. **啟動 Gateway**：`openclaw gateway start`
4. **健康檢查**：`openclaw doctor`

👉 **詳見**：[20_OpenClaw_Integration](20_OpenClaw_Integration.md)

---

## 8. 分靈體設定模板

在 Vault 的 `00_Self_Introduction/分靈體_Horcrux/` 目錄中提供了完整的分靈體設定模板：

| 檔案 | 用途 |
|:---|:---|
| `HORCRUX_TEMPLATE.md` | 身份、環境變數、靈魂精簡版模板 |
| `HORCRUX_RULES.md` | 權限矩陣與行為規範 |

---
> 返回 [總覽](00_Overview.md)
