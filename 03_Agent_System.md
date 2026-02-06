# 03_Agent_System: 配合 AI 的 PARA 架構

> **給 Agent 一個整齊的家，它才不會把你的檔案亂丟。**

---

## 為什麼需要 Agent 專屬資料夾？

我們通常有自己的文件習慣，但 AI 需要更嚴格的結構才能有效檢索。我們建立一個專屬目錄 `🧠_Agent_System`，這是 AI 的「領地」。

## PARA 架構的 AI 化變體

我們基於 Tiago Forte 的 PARA (Projects, Areas, Resources, Archives) 方法，做了一些微調以適應 AI：

### 0. 系統層 (`00_` & `99_`)
- **`00_Self_Introduction/`**：核心身份 (Identity, Soul, User)。
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
