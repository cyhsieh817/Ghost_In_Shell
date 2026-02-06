# 10_Onboarding: 新 Agent 入職指引

> **讓新 Agent 快速融入大腦系統。**

---

## 新 Agent 首次連線流程

### 1. 生成 Device ID

Agent 自動生成 **16 位元隨機英數字串**：
```
範例：A7x9K2mP4qR8sT1w
```

### 2. 建立識別檔

在 `DEVICES/` 建立 `[Device ID].md`：
```markdown
# Device: [Device ID]
- Agent: {{AGENT_NAME}}
- 首次連線: [ISO 8601]
- 優先權: SECONDARY
```

### 3. 閱讀核心規範

| 順序 | 檔案 |
|:---:|------|
| 1️⃣ | `IDENTITY.md` |
| 2️⃣ | `SOUL.md` |
| 3️⃣ | `AGENTS.md` |
| 4️⃣ | `ACCESS_POLICY.md` |
| 5️⃣ | `MEMORY.md` |

### 4. 記錄註冊

在 `Audit_Log.md` 記錄：
```
| 時間 | 裝置 | 動作 | 備註 |
| --- | --- | REGISTER | 新裝置加入 |
```

---

## 完整指引

👉 [🚀 ONBOARDING.md](file:///🧠_Agent_System/ONBOARDING.md)

---

> 返回 [總覽](00_Overview.md)
