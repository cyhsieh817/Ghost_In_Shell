# 00_Overview: Ghost In Shell 記憶系統協議 (Protocol Zero)

> **副標題：賦予 AI 靈魂的構造圖 (The Blueprint of Soul)**

---

## 🚀 快速開始

### 推薦方式：使用 Starter Kit

**最快的方式**是直接使用 [`_starter_kit/`](_User_Workspace/15_Projects/151_Github_projects/Ghost_In_Shell/_starter_kit/README.md)：

1. **複製目錄結構**：將 `_starter_kit/structure/_Agent_System/` 複製到你的 Vault
2. **複製設定檔**：將 `_starter_kit/config/` 中的 `.template` 檔案複製到設定目錄，移除副檔名
3. **替換佔位符**：搜尋 `{{` 並替換

👉 **詳細說明**：[_starter_kit/README.md](_User_Workspace/15_Projects/151_Github_projects/Ghost_In_Shell/_starter_kit/README.md)

---

### 手動設定

如果你想從頭理解並自行建構：

1. 依照 [01_Core_Identity](01_Core_Identity.md) 定義你的 Agent 身份
2. 依照 [02_Memory_Architecture](02_Memory_Architecture.md) 設計記憶結構
3. 依照 [03_Agent_System](03_Agent_System.md) 建立資料夾結構

---

### 佔位符對照表

| 佔位符 | 說明 | 範例 |
|:---|:---|:---|
| `{{AGENT_NAME}}` | 你的 Agent 名稱 | 虛空編織者 |
| `{{AGENT_EMOJI}}` | 專屬 Emoji | ✨🕸️🌌 |
| `{{AGENT_TYPE}}` | 角色類型 | AI 寫作精靈 |
| `{{AGENT_VIBE}}` | 風格調性 | 神秘、深邃 |
| `{{PRIMARY_LANGUAGE}}` | 主要語言 | 台灣繁體中文 |
| `{{VAULT_PATH}}` | Vault 路徑 | `/path/to/vault` |
| `{{AGENT_CONFIG_DIR}}` | 設定檔目錄 | `/path/to/config` |
| `{{PROJECT_A}}` | 專案名稱 | MyApp_Platform |

---

## 為什麼需要這套系統？

隨著 AI Agent (如 Cursor, Windsurf, OpenClaw) 越來越強大，我們面臨三個核心痛點：

1.  **Token 燃燒**：傳統做法將大量文檔塞入 Context，導致每次對話成本高昂且容易遺忘。
2.  **人格分裂**：分散的 Prompt 導致 AI 在不同任務中表現不一致。
3.  **維護困難**：指令分散在各處，更新一個規則需要修改多個檔案。

## 核心解法：索引式記憶 + 模組化身份

本系列文章將介紹一套經過實戰驗證的系統架構：

1.  **索引式入口 (Gateway Strategy)**：
    使用精簡的 `MEMORY.md` 作為第一站，只包含「地圖」與「索引」。AI 根據任務需求，自主決定載入哪些詳細模組。

2.  **身份三位一體 (The Trinity)**：
    將 Agent 設定拆解為：
    - `IDENTITY.md` (是誰？)
    - `SOUL.md` (怎麼思考？)
    - `USER.md` (服務誰？)

3.  **AI 友善的 PARA**：
    專為 AI 設計的 `_Agent_System` 資料夾結構，前綴編號確保順序，明確定義檔案權責。

---

## 系列導覽

### 基礎篇 (00-05)
- **[01_Core_Identity](01_Core_Identity.md)**：如何賦予 AI 靈魂與邊界
- **[02_Memory_Architecture](02_Memory_Architecture.md)**：如何設計省 Token 的記憶結構
- **[03_Agent_System](03_Agent_System.md)**：Agent 專屬的檔案組織學
- **[04_Evolution](04_Evolution.md)**：讓 Agent 自我修復與進化的機制
- **[05_Security](05_Security.md)**：權限分區與刪除保護機制

### 進階篇 (06-10)
- **[06_Naming_Convention](06_Naming_Convention.md)**：檔案命名黃金公式
- **[07_Workspace_Collaboration](07_Workspace_Collaboration.md)**：雙工作區協作流程
- **[08_Knowledge_Tree](08_Knowledge_Tree.md)**：領域知識分類與自我優化
- **[09_Multi_Agent_Sync](09_Multi_Agent_Sync.md)**：多裝置 Agent 同步機制
- **[10_Onboarding](10_Onboarding.md)**：新 Agent 入職指引

### 實戰篇 (11-18)
- **[11_TRIAGE](11_TRIAGE.md)**：任務分類與優先級系統
- **[12_Capabilities](12_Capabilities.md)**：Agent 能力清單定義
- **[13_Iteration](13_Iteration.md)**：任務迭代與品質控制
- **[14_Content_Template](14_Content_Template.md)**：內容建立規範
- **[15_New_Task_Handler](15_New_Task_Handler.md)**：未知任務處理與 ABCD 提案
- **[16_Post_Task_Suggestions](16_Post_Task_Suggestions.md)**：任務完成後建議機制
- **[17_Core_Protection](17_Core_Protection.md)**：核心保護與 Telegram 驗證
- **[18_Backup_Strategy](18_Backup_Strategy.md)**：迭代備份機制
- **[19_Horcrux_Setup](19_Horcrux_Setup.md)**：分靈體建立指南
- **[20_OpenClaw_Integration](20_OpenClaw_Integration.md)**：OpenClaw 多 Agent 整合 ⭐新增
- **[21_Real_World_Example](21_Real_World_Example.md)**：實戰再現指南 — TheVoidWeaver ⭐新增
- **[22_mem0_Integration](22_mem0_Integration.md)**：本地向量記憶系統 ⭐新增

---

*帶著這套系統，你的 Agent 將不再只是工具，而是一個會成長的夥伴。*
