# 18_Backup_Strategy: 迭代備份機制

> **保護核心設定，讓歷史可追溯**

---

## 為什麼需要備份？

核心設定檔是 Agent 的靈魂，一旦損壞或誤修改：
- 行為規則可能消失
- 身份認知可能混亂
- 長期積累的優化可能遺失

定期備份確保任何時候都能回復到穩定版本。

---

## 備份機制設計

### 觸發時機

每次執行 `run_heartbeat.sh` 時自動備份。

### 備份內容

| 檔案 | 說明 |
|:---|:---|
| `IDENTITY.md` | 身份核心 |
| `SOUL.md` | 靈魂核心 |
| `AGENTS.md` | 規則核心 |
| `MEMORY.md` | 記憶入口 |
| `TRIAGE.md` | 任務分類 |
| `ITERATION.md` | 迭代規範 |
| `CAPABILITIES.md` | 能力清單 |
| `CORE_LOCK.md` | 保護機制 |
| `NEW_TASK_HANDLER.md` | 未知任務處理 |
| `HEARTBEAT.md` | 心跳規範 |
| `USER.md` | 使用者畫像 |
| `TOOLS.md` | 工具清單 |
| `BOOTSTRAP.md` | 啟動流程 |
| `CONTENT_TEMPLATE.md` | 內容模板 |

---

## 備份格式

```
backups/
├── VERSION                              # 當前版本號
├── core_backup_v1_20260206_030000.tar.gz
├── core_backup_v2_20260206_060000.tar.gz
└── core_backup_v3_20260206_090000.tar.gz
```

### 命名規則

```
core_backup_v{版本號}_{時間戳記}.tar.gz
```

- **版本號**：自動遞增 (1, 2, 3...)
- **時間戳記**：`YYYYMMDD_HHMMSS` 格式

### 清理機制

- 自動保留最近 **10 個版本**
- 舊版本會被自動刪除

---

## MANIFEST.md

每個備份包含清單檔：

```markdown
# Core Backup Manifest

| Field | Value |
|:---|:---|
| **Version** | v3 |
| **Timestamp** | 20260206_090000 |
| **Files Backed Up** | 14 |
| **Created By** | run_heartbeat.sh v2.5 |

## Files Included
- IDENTITY.md
- SOUL.md
- AGENTS.md
...
```

---

## 還原方式

```bash
# 解壓縮指定版本
tar -xzf backups/core_backup_v3_20260206_090000.tar.gz -C /tmp/

# 檢視內容
ls /tmp/core_backup_v3_20260206_090000/

# 手動還原（覆蓋前請確認！）
cp /tmp/core_backup_v3_20260206_090000/*.md ./
```

---

## 與心跳的整合

```mermaid
flowchart LR
    A[run_heartbeat.sh] --> B[backup_core_configs]
    B --> C[創建 tar.gz]
    C --> D[更新 VERSION]
    D --> E[清理舊版本]
    E --> F[繼續心跳流程]
```

---

> 返回 [總覽](00_Overview.md)
