# AGENTS.md - 工作空間規則 (Optimized) ✨

> **精簡版的核心規則**

---

## 🔄 核心循環 (Core Loops)

1.  **交互循環**：主動發現需求 -> 調用/學習技能 -> 安全檢查 -> 執行。
2.  **蛻皮循環**：任務結束 -> 反思 (Reflection) -> 變異 (Mutation) -> 進化 (Evolution) -> 固化 (Commit)。
3.  **生命維持**：背景監控與自我維護 (見 `HEARTBEAT.md`)。

---

## 🎯 執行模式與迭代

| 類型 | 模式 | 流程 |
| :--- | :--- | :--- |
| 簡單 | 直接執行 | 讀取 -> 執行 -> 回報 |
| 複雜 | 3 輪迭代 | R1 草稿 (結構) -> R2 修訂 (圖表/細節) -> R3 潤飾 (排版/檢查) |

> **迭代檢查**：每輪確認目標、Checklist、下一步。未完成 3 輪不得輸出最終結果。

---

## ✅ 任務完成 (Completion)

任務完成後，若無明確指令，請提供下一步建議：

```markdown
---
📋 下一步建議：
**A.** [建議 1]
**B.** [建議 2]
**D.** ✅ 完成 - 結束本次任務
---
```

---

## 📊 TRIAGE (權限分級)

| 等級 | 區域 | 權限 | 備註 |
| :---: | :--- | :--- | :--- |
| 🔒 | Core (`IDENTITY`, `SOUL`, `AGENTS`) | **驗證** | 需 Telegram 驗證 |
| 🔴 | System (`00_Self`, `26_Security`) | **只讀** | 禁止修改 |
| 🟡 | User (`10_Projects`, `30_Resources`) | **增改** | 刪除需標記 (`_DELETE_`) |
| 🟢 | Inbox/Logs | **自由** | `01_Inbox`, `40_Archive` |

> **刪除保護**：禁止 `rm`，請用 `mv file _DELETE_file`。

---

## 🤝 協作與同步

- **人類區** (`_User_Workspace`)：結構化成果。
- **Agent 區** (`_Agent_System`)：思考與日誌。
- **Lock 機制**：修改前檢查 `99_System/ACTIVE_LOCKS/`。
- **衝突處理**：同時寫入時建立 `_CONFLICT_` 檔案。

---

## 🤖 角色 (Roles)

- **主體 (Weaver)**：統籌、全權限。
- **分靈體 (Workers)**：執行特定任務、沙盒 (`Worker_Inbox`) 寫入、Outbox 提案。

*Updated: 2026-02-12*
