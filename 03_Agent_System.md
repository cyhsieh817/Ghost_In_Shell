# 03_Agent_System: 配合 AI 的 PARA 架構

> **給 Agent 一個整齊的家，它才不會把你的檔案亂丟。**

---

## 為什麼需要 Agent 專屬資料夾？

我們通常有自己的文件習慣，但 AI 需要更嚴格的結構才能有效檢索。我們建立一個專屬目錄 `🧠_Agent_System`，這是 AI 的「領地」。

## PARA 架構的 AI 化變體

我們基於 Tiago Forte 的 PARA (Projects, Areas, Resources, Archives) 方法，做了一些微調以適應 AI：

### 0. 系統層 (`00_` & `99_`)
- **`00_Self_Introduction/`**：核心身份 (Identity, Soul, User)。
  - 本體設定檔直接放在根目錄
  - `分靈體_Horcrux/`：分靈體的模板與規則（詳見 [19_Horcrux_Setup](19_Horcrux_Setup.md)）
  - `DEVICES/`：裝置識別與註冊
- **`01_Inbox/`**：AI 收件匣，未分類的任務先丟這。
- **`99_System/`**：運作日誌、模板、設定檔。

### 1. Projects (`10_Projects/`) - 有時效的任務
- **特色**：有明確目標、有截止日。
- **編號技巧**：使用 `10_`, `11_` 等前綴，避免 AI 排序混亂。
- **範例**：`10_{{PROJECT_A}}`, `15_{{PROJECT_B}}`

### 2. Areas (`20_Areas/`) - 持續的責任
- **特色**：長期維護、無截止日。
- **AI 應用**：
    - `25_Agent_Collaboration/`：多 Agent 之間的溝通協議。
    - `26_Security/`：API Key 管理、白名單。
    - `27_Communication/`：Telegram/Line 設定。

#### 角色與權限策略
此處定義了不同 Agent 角色（主體與分靈體）的職責與權限。

| 角色 | 名稱 | 職責 | 權限概述 |
|:---|:---|:---|:---|
| **主體** | 虛空編織者 | 複雜任務、整合資訊、統籌協調、核心系統配置管理 | 對整個 Vault 擁有完整讀寫刪權限，可修改核心配置檔案。 |
| **分靈體** | 各子 Agent | 執行特定任務，通常在沙盒中工作 | 預設對所有公開資料只讀；寫入操作僅限於其專屬 `Worker_Inbox` 沙盒；對 `📂_User_Workspace/03_Agent_Outbox/` 有新增/修改權限，但最終歸檔需主體或人類確認。無法修改核心配置檔案。 |

**情緒隔離原則**：前鋒的冒險，不應動搖主力的心神。

**重要配對與保護**：
- 每個分靈體應與 `/Users/cyuh/Library/CloudStorage/GoogleDrive-cyhsieh@yc-biotech.net/My Drive/TheVoidWeaverObisidain/🧠_Agent_System/00_Self_Introduction/DEVICES` 中定義的裝置身份或 Agent ID 進行唯一配對。
- 分靈體的身份資訊及其 `Worker_Inbox` 的對應關係不應被隨意修改。
- 核心配置文件 (如 `IDENTITY.md`, `SOUL.md`, `AGENTS.md`, `CORE_LOCK.md`) 需透過額外驗證（如 Telegram 雙因素驗證）才能修改，確保其不可篡改性。


### 3. Resources (`30_Resources/`) - 知識庫
- **特色**：參考資料、技能書、模板。
- **重要目錄**：
    - `35_Skills/`：存放 Agent 的特殊技能定義 (SKILL.md)。
    - `36_Templates/`：文件模板。

### 4. Archives (`40_Archive/`) - 歷史區
- **原則**：這層通常不讓 AI 主動讀取，避免舊資訊干擾。
- **動作**：專案結束後，整包移至此。

## 機器可讀性最佳實踐 (Machine Readability)

1.  **README.md 是標配**：每個資料夾下都要有一個 `README.md`，用一句話解釋這個資料夾在幹嘛。
2.  **明確的路徑引用**：在文件中引用其他檔案時，盡量用相對路徑或完整路徑，不要只寫檔名。
3.  **一致的命名**：`Snake_Case` (如 `daily_log.md`) 比 `Space Case` 更容易被程式碼解析。

---

> **下一步**：系統建好後，如何讓它持續變強？下一篇我們談談 [Evolution & Heartbeat](04_Evolution.md)。
