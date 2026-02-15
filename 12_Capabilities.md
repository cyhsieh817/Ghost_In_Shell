# 12_Capabilities: Agent 能力清單

> **定義 Agent 能做什麼、不能做什麼**

---

## 為什麼需要能力清單？

明確定義 Agent 的能力邊界，讓它：
1. 知道哪些任務可以直接處理
2. 哪些需要安裝工具
3. 哪些必須交給人類

---

## ✅ 內建能力 (Built-in)

| 能力 | 狀態 | 說明 |
|:---|:---:|:---|
| **檔案讀寫** | ✅ | 讀取/建立/修改檔案 |
| **知識查詢** | ✅ | 搜尋與引用 `30_Resources/` |
| **文字生成** | ✅ | 撰寫文章、摘要、分析 |
| **分類歸檔** | ✅ | 整理 Inbox/Archive |

---

## 🌐 瀏覽工具 (Browser & Web)

| 工具 | 設定 | 用途 |
|:---|:---|:---|
| **web_search** | `{{WEB_SEARCH_TOOL}}` | 網路資料查詢 |
| **Browser** | `{{BROWSER_PROFILE}}` | 自動化網頁瀏覽 |

### 瀏覽權限規則

與 TRIAGE 系統整合：

| 等級 | 類型 | 說明 |
|:---:|:---|:---|
| 🟢 **AUTO** | 資料查詢 | `web_search` 純文字搜尋 |
| 🟡 **CONFIRM** | 頁面瀏覽 | 開啟網站讀取（無互動） |
| 🔴 **ASK** | 互動操作 | 登入、填表、提交 |

---

## 💻 開發與編碼 (Coding & Dev Tools)

| 工具 | 設定 | 用途 |
|:---|:---|:---|
| **Opencode** | `send_to_opencode.sh` | 執行複雜指令、編輯程式碼 |
| **Terminal** | `run_command` | 執行系統 Shell 指令 |

### Opencode 權限分級

| 等級 | 類型 | 說明 |
|:---:|:---|:---|
| 🟢 **READ** | 讀取/分析 | `ls`, `cat`, `grep` 等唯讀操作 |
| 🟡 **EXEC** | 執行測試 | `npm test`, `cargo run` 等無副作用指令 |
| 🔴 **WRITE** | 修改代碼 | `write_to_file`, `sed` 等修改操作 |

---

## ⚠️ 需安裝/確認 (Pending)

| 能力 | 工具需求 | 狀態 |
|:---|:---|:---:|
| **發送訊息** | Telegram Bot API | ⚠️ 需設定 |
| **發送 Email** | SMTP / API | ⚠️ 需設定 |

---

## 🎨 圖片與視覺化 (Visual Content)

| 工具 | 狀態 | 用途 |
|:---|:---:|:---|
| **Mermaid** | ✅ | 流程圖、架構圖 (內建 Markdown) |
| **AI Image Gen** | ⚠️ | 視模型能力而定 |
| **Web Image Ref** | 🟡 | 引用網路圖片 (需標來源) |

---

## ❌ 不具備 (Human Required)

| 任務類型 | 原因 |
|:---|:---|
| **登入第三方服務** | 需要人類 2FA 或驗證碼 |
| **金融交易** | 安全考量，絕對禁止自動化 |
| **實體操作** | 無硬體控制能力 |

---

## 與 TRIAGE 的整合

能力查找發生在 TRIAGE 分類之前：

```
任務輸入 → 能力查找 → TRIAGE 分類
              ↓
    ✅ 可執行 → 繼續分類
    ⚠️ 需安裝 → 🟡 CONFIRM
    ❌ 無法  → 🔴 ASK（轉人類待辦）
```

---

## 實作模板

👉 [CAPABILITIES.md.template](CAPABILITIES.md.template)

---

> 返回 [總覽](00_Overview.md)
