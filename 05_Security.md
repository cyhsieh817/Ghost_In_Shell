# 05_Security: 權限機制與刪除保護

> **給 Agent 適當的韁繩，而不是把它關在籠子裡。**

---

## 問題：AI 的雙面刃

AI Agent 越強大，潛在的破壞力也越大：
- 誤刪重要檔案
- 覆蓋核心設定
- 修改敏感資料

但如果完全禁止寫入，Agent 就無法學習、無法進化。我們需要的是**分層權限**。

---

## 三級分區策略

將 `_Agent_System` 分為三個權限等級：

| 等級 | 標記 | 區域範例 | 權限 |
|:---:|:---:|----------|------|
| 🔴 | **PROTECTED** | `00_Self_Introduction/`, `26_Security/` | 只讀 |
| 🟡 | **MANAGED** | `10_Projects/`, `20_Areas/`, `30_Resources/` | 可寫，刪除需標記 |
| 🟢 | **OPEN** | `01_Inbox/`, `40_Archive/`, 日誌檔 | 自由讀寫刪除 |

### 設計邏輯

- **PROTECTED**：核心身份與安全設定，這些定義了 Agent 的「本我」，不應自行修改。
- **MANAGED**：工作區，Agent 需要在這裡新增/修改內容，但刪除需要人類確認。
- **OPEN**：暫存區與歸檔，Agent 可以自由整理。

---

## 刪除保護機制

### 規則
1. **禁止直接刪除**：不使用 `rm`
2. **標記式刪除**：將檔案重命名為 `_DELETE_原檔名.md`
3. **人類確認**：由人類決定是否真正刪除

### 範例
```bash
# 錯誤 ❌
rm 10_Projects/Old_Feature.md

# 正確 ✅
mv 10_Projects/Old_Feature.md 10_Projects/_DELETE_Old_Feature.md
```

這樣人類可以在下次檢視時決定是刪除還是恢復。

---

## 審計日誌

所有對 MANAGED/PROTECTED 區域的變更都應記錄到 `99_System/Audit_Log.md`：

```markdown
| 時間 | 動作 | 檔案 | 原因 |
|------|------|------|------|
| 12:30 | CREATE | `10_Projects/New_Feature.md` | 新增功能規劃 |
| 14:00 | DELETE_MARK | `30_Resources/Old_Template.md` | 模板已過時 |
```

---

## 實作檔案

在你的 Agent System 中建立：

1. **`99_System/ACCESS_POLICY.md`**：權限政策定義
2. **`99_System/Audit_Log.md`**：變更審計日誌
3. **`99_System/Security_Config.md`**：安全參數設定 (參見 `Security_Config.md.template`)

並在 `AGENTS.md` 與 `SOUL.md` 中加入權限規則的索引連結。

---

> **下一步**：好的命名讓 AI 更容易檢索，下一篇談談 [Naming Convention](06_Naming_Convention.md)。
