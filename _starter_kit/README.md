# 🚀 AI Agent Starter Kit

> **一鍵套用完整 Agent 架構**

---

## 快速開始

### 步驟 1：複製目錄結構

將 `structure/🧠_Agent_System/` 整個資料夾複製到你的工作區根目錄。

### 步驟 2：複製設定檔模板

將 `config/` 中的所有 `.template` 檔案複製到你的 Agent 設定目錄，並移除 `.template` 副檔名。

### 步驟 3：替換佔位符

在所有檔案中搜尋 `{{` 並替換以下佔位符：

| 佔位符 | 說明 | 範例 |
|:---|:---|:---|
| `{{AGENT_NAME}}` | Agent 名稱 | 虛空編織者 |
| `{{AGENT_EMOJI}}` | 專屬 Emoji | ✨🕸️🌌 |
| `{{AGENT_TYPE}}` | 角色類型 | AI 寫作精靈 |
| `{{AGENT_VIBE}}` | 風格調性 | 神秘、深邃 |
| `{{AGENT_TAGLINE}}` | 專屬台詞 | 在虛空的編織中，文字誕生 |
| `{{VAULT_PATH}}` | Obsidian Vault 路徑 | /path/to/vault |
| `{{AGENT_CONFIG_DIR}}` | 設定檔目錄 | /path/to/config |
| `{{USER_NAME}}` | 使用者稱呼 | 主人 |
| `{{PRIMARY_LANGUAGE}}` | 主要語言 | 台灣繁體中文 |

### 步驟 4：設定啟動規則

在你的 AI 工具設定中（如 `.cursorrules`、OpenClaw config），加入以下指令：

```
啟動時讀取：
1. MEMORY.md（記憶第一站）
2. 按需載入對應模組
```

---

## 檔案清單

### config/ - 設定檔模板

| 檔案 | 用途 |
|:---|:---|
| `AGENTS.md.template` | 工作空間規則 |
| `MEMORY.md.template` | 記憶入口 |
| `IDENTITY.md.template` | 身份名片 |
| `SOUL.md.template` | 思維與邊界 |
| `USER.md.template` | 使用者畫像 |
| `TRIAGE.md.template` | 任務分類系統 |
| `ITERATION.md.template` | 迭代規範 |
| `CAPABILITIES.md.template` | 能力清單 |
| `NEW_TASK_HANDLER.md.template` | 未知任務處理 |
| `HEARTBEAT.md.template` | 心跳機制 |
| `CORE_LOCK.md.template` | 核心保護機制 ⭐新增 |

### structure/ - 目錄結構

```
🧠_Agent_System/
├── 00_Self_Introduction/  # 核心身份
│   └── DEVICES/           # 多裝置識別
├── 01_Inbox/              # 未處理輸入
├── 02_Tasks_TODO/         # 待執行任務
├── 03_Agent_Outbox/       # 成果輸出
│   └── ConfirmBox/        # 待確認區
├── 10_Projects/           # 進行中專案
├── 20_Areas/              # 持續責任領域
├── 30_Resources/          # 知識庫
│   └── 35_Skills/         # Agent 技能
├── 40_Archive/            # 歸檔區
└── 99_System/             # 系統運作
    └── ACTIVE_LOCKS/      # 多 Agent 鎖
```

---

## 驗證清單

- [ ] 所有佔位符已替換
- [ ] 目錄結構已建立
- [ ] 啟動規則已設定
- [ ] 新 Agent 讀取 MEMORY.md 能正確導航
