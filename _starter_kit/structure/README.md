# 🧠_Agent_System 目錄結構

> 此為 Agent 專屬工作區的標準目錄結構

---

## 目錄說明

| 目錄 | 用途 |
|:---|:---|
| `00_Self_Introduction/` | 核心身份（IDENTITY, SOUL, USER, DEVICES） |
| `01_Inbox/` | 未處理輸入，Agent 可自動分類 |
| `02_Tasks_TODO/` | 人類指派的待辦，執行前需詢問 |
| `03_Agent_Outbox/` | Agent 成果輸出區 |
| `03_Agent_Outbox/ConfirmBox/` | 待人類確認的成果 |
| `10_Projects/` | 進行中專案 |
| `20_Areas/` | 持續責任領域 |
| `30_Resources/` | 知識庫與資源 |
| `30_Resources/35_Skills/` | Agent 技能定義 |
| `40_Archive/` | 歸檔區（Agent 通常不主動讀取） |
| `99_System/` | 系統運作（日誌、設定、鎖） |
| `99_System/ACTIVE_LOCKS/` | 多 Agent 同步鎖 |

---

## 權限分區

| 區域 | 權限 |
|:---:|:---|
| 🔴 | `00_Self_Introduction/` - 只讀 |
| 🟡 | `10_Projects/`, `20_Areas/`, `30_Resources/` - 可增改，刪除需標記 |
| 🟢 | `01_Inbox/`, `40_Archive/`, 日誌檔 - 自由操作 |

---

## 使用方式

1. 將整個 `🧠_Agent_System/` 資料夾複製到你的 Vault 根目錄
2. 依需求建立子資料夾（如 `10_Projects/10_MyProject/`）
3. 在各資料夾中建立 `README.md` 描述用途
