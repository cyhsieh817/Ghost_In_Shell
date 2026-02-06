# 02_Memory_Architecture: 記憶架構

> **用「索引」取代「全本」，打造省 Token 的高效大腦。**

---

## 傳統問題：Token 黑洞

最常見的做法是把所有專案文件、筆記都丟給 AI。結果：
- **Token 爆炸**：每次對話成本極高。
- **注意力分散**：AI 在海量資訊中找不到重點。
- **遺忘**：Context Window 滿了之後，前面的重要資訊被丟棄。

## 解法：Gateway Strategy (入口策略)

我們不給 AI 看整座圖書館，只給它看「目錄卡」。

### 1. MEMORY.md - 唯一的記憶入口

`MEMORY.md` 不應該包含詳細內容，它只是一個 **Router (路由器)**。

**範例模板：**
```markdown
# {{AGENT_NAME}} - 核心記憶

> **此檔案為記憶系統的第一站入口**
> 按需載入對應模組

## 🗺️ 記憶地圖
- **身份**：`00_Self_Introduction/IDENTITY.md`
- **協作**：`20_Areas/25_Agent_Collaboration/Collaboration_Protocol.md`
- **專案**：`10_Projects/` (見下表)

## 📂 專案索引
| 專案 | 路徑 |
|------|------|
| {{PROJECT_A}} | `10_Projects/10_{{PROJECT_A}}/` |
| {{PROJECT_B}} | `10_Projects/15_{{PROJECT_B}}/` |
```

### 2. On-Demand Loading (按需載入)

在 `AGENTS.md` 或 System Prompt 中設定規則：

> "啟動時只讀取 `MEMORY.md`。根據任務需求，再自行決定讀取哪個子模組。"

**情境模擬：**
1. **User**: "幫我優化 {{PROJECT_A}} 的登入介面。"
2. **AI (讀 MEMORY.md)**: "收到。查閱索引，{{PROJECT_A}} 在 `10_Projects/10_{{PROJECT_A}}/`。"
3. **AI (讀子目錄)**: "已載入專案規範。開始分析..."

這樣 AI 只花了讀取索引的 Token，而不是整個 Vault 的 Token。

### 3. 精簡化技巧

- **用表格 (Table)**：Markdown 表格比條列式更省 Token，且結構清晰。
- **去除冗言**：不要寫 "這個檔案是用來..."，直接寫 "用途：..."。
- **連結 (Link)**：善用檔案路徑連結，AI 工具通常能識別並快速跳轉。

---

> **下一步**：有了索引，檔案本身該怎麼歸檔？下一篇我們談談 [Agent System Structure](03_Agent_System.md)。
