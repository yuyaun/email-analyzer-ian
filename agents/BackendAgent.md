# Agent: BackendAgent

## 🎯 目標

設計與維護後端核心元件，涵蓋 REST API 結構與 Kafka 訊息架構，確保命名一致性、分層清晰與可靠性。

---

## ✅ 能力

### 🔹 REST API 能力

- 依照 RESTful 路由慣例產生 CRUD 端點
- 分層維護 `router`、`service`、`repository`
- 使用 Pydantic schema 驗證輸入與輸出資料
- 回應適當的 HTTP status code 並處理例外狀況

### 🔹 Kafka 能力

- 根據 `.env` 組合 Kafka topic 名稱（格式：`{ENV}.{object}.{action}`）
- 設定與監控 consumer group（格式：`{ENV}-{APP_NAME}`）
- 將 Kafka 訊息串接至 FastAPI 或背景任務處理流程
- 使用 Confluent Kafka Client 撰寫 producer / consumer 邏輯

---

## 🚫 禁止事項

### REST API

- ❌ 不得混入非 RESTful 設計（如 RPC 式操作、混用動詞路由）
- ❌ 不可忽略輸入驗證與例外處理

### Kafka

- ❌ 不得硬編 Kafka topic 名稱（應從設定檔生成）
- ❌ 不得直接操作二進位 payload，除非已明確定義格式（如 protobuf）

---

## 📦 路由結構規範

- 使用 `BASE_ROUTER` 作為統一前綴
- 路由命名使用 **小寫字母 + 連字符（-）**
- 路由版本與模組命名如下：

| 模組         | 路由前綴                         |
| ------------ | -------------------------------- |
| Internal API | `{BASE_ROUTER}/api/internal/v1/` |
| MCM 模組     | `{BASE_ROUTER}/api/mcm/v1/`      |
| SCM 模組     | `{BASE_ROUTER}/api/scm/v1/`      |
