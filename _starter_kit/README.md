# TheViodWeaver - AI Agent Core 🧠

> **Agent 的靈魂與核心配置庫**
> 這裡是 ViodWeaver (Antigravity) 的 "Source Code"，定義了它的人格、記憶結構與運作邏輯。

## 📂 核心檔案導覽

### 核心定義 (Root)
| 檔案 | 用途 | 說明 |
|------|------|------|
| **`IDENTITY.md`** | **我是誰** | 核心身份定義、名稱、版本。 |
| **`SOUL.md`** | **靈魂** | 人格特質、價值觀、語言風格。 |
| **`USER.md`** | **使用者** | 對 User (CYuH) 的理解與偏好設定。 |
| **`MEMORY.md`** | **記憶地圖** | 檔案系統結構與載入策略 (**Dual-File Standard**)。 |
| **`AGENTS.md`** | **運作規則** | 啟動流程、Loop 架構、迭代規範。 |
| **`TRIAGE.md`** | **任務分類** | 任務風險評估與分類矩陣 (AUTO/CONFIRM/ASK)。 |
| **`HEARTBEAT.md`** | **心跳機制** | 定期自我檢查與維護的 SOP。 |
| **`CORE_LOCK.md`** | **安全鎖** | 防止核心被意外修改的機制。 |

### 系統目錄
| 目錄 | 用途 |
|------|------|
| **`scripts/`** | 系統腳本 (`run_heartbeat.sh`, `git_backup.sh` 等) |
| **`config/`** | 設定檔 (`security_config.json`, `mcporter.json`) |
| **`logs/`** | (Legacy) 舊日誌歸檔。新日誌已導向 Vault `991_Logs/` |

## 🔗 系統架構

本核心庫 (`TheViodWeaver`) 會同步至 Obsidian Vault 的 `_Agent_System/00_Self_Introduction/`，作為 Agent 的「自我意識」來源。

- **本體 (Source)**: `{{AGENT_WORKSPACE}}`
- **分靈體 (Runtime)**: `Obsidian/_Agent_System/00_Self_Introduction`

## 🛠️ 維護指令

- **執行心跳**: `./scripts/run_heartbeat.sh`
- **同步核心**: 執行 `scripts/sync_core.sh` (若有的話)
- **更新靈魂**: 修改 `SOUL.md` 後需重新 reload context。

---
*Created by CYuH & Antigravity*
