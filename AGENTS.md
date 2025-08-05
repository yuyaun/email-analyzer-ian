# AGENTS.md

本專案使用多個 Agent 概念模組，協助進行自動化開發、重構與文件生成。

## 🧠 Agents 一覽

| Agent 名稱       | 功能描述                           | 檔案位置                     |
| ---------------- | ---------------------------------- | ---------------------------- |
| KafkaBot         | 設定與使用 Kafka topic 與 consumer | `agents/KafkaBot.md`         |
| ApiBot           | 建立 REST API 並維持一致命名與結構 | `agents/ApiBot.md`           |
| DocsBot          | 撰寫 README、docstring、文件產生器 | `agents/DocsBot.md`          |
| RefactorBot      | 重構舊有程式碼、改善可讀性與品質   | `agents/RefactorBot.md`      |
| TestGenie        | 自動產生 pytest 測試               | `agents/TestGenie.md`        |
| BugHunter        | 偵錯與分析程式錯誤                 | `agents/BugHunter.md`        |
| RequirementAgent | 需求分析與功能規劃                 | `agents/RequirementAgent.md` |
| FrontendAgent    | 前端開發與 Vue.js 整合             | `agents/FrontendAgent.md`    |

## 💡 說明

- 每個 agent 都為 AI 專屬的角色設定檔
- 可轉換為 `.json` 形式供自動化工具使用
- 系統架構為 `Architecture.mmd`
- 專案範圍為 `PROJECT_SCOPE.md`，包含功能、技術架構、部署方式等。
- 專案資料夾結構簡述：

  - `frontend/`：前端程式碼（Vue.js 等）
  - `backend/`：後端程式碼（FastAPI 等）
  - `agents/`：AI Agent 設定與模組
  - `spec/`：需求規格與技術文件
  - `k8s/`：Kubernetes 部署設定

- 新增資料夾說明：
  - `agents/`：存放各類自動化 AI Agent 角色檔案
  - `spec/`：存放專案需求、API 規格、架構設計等文件

## 前端技術需求 (Frontend Technical Requirements)

- 使用 Vue.js 實作前端頁面
- 使用 Axios 發送 API 請求
- 使用 Vue Router 管理路由
- 使用 Element UI 或其他 UI 框架提升使用者體驗

## 技術需求（Technical Requirements）

- 使用 FastAPI 實作 API
- 整合 LINE Login API 進行用戶驗證
- 使用 PostgreSQL 儲存團購參與者資料
- 使用 Alembic 管理資料庫遷移
- 使用 Kafka 發佈事件（如有需要）
- 使用 Docker Compose 管理開發環境
- 使用 pytest 進行單元測試
- 使用 Pydantic 進行資料驗證
- 使用 SQLAlchemy ORM 進行資料庫操作
- 使用 Uvicorn 作為 ASGI 伺服器
- 使用 Dockerfile 建立開發環境映像檔
