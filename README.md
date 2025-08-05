# Email Analyzer 專案

Email Analyzer 是一個示範專案，展示如何結合 FastAPI、Kafka、PostgreSQL 與大型語言模型（LLM），提供郵件內容分析與建議功能。系統採用微服務架構，並使用多個 AI Agent 角色協助開發與文件產生。

## 功能特色
- 檔案上傳（支援 `.txt` / `.html`，大小上限 1MB）
- 郵件內容欄位驗證與冷卻時間限制
- JWT 註冊與驗證流程
- Rate Limit 控制與重複內容檢查
- 整合 OpenAI GPT-4o-mini 進行內容分析與生成

## 專案結構
```
.
├── agents/            # AI Agent 設定檔
├── backend/           # FastAPI 後端服務
├── spec/              # 需求規格與技術文件
├── Architecture.svg   # 系統架構圖
└── PROJECT_SCOPE.md   # 專案範圍與時程規劃
```

## 快速開始
### 1. 安裝依賴
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. 啟動開發環境
使用 Docker Compose 啟動 PostgreSQL 與 Kafka：
```bash
cd backend
docker-compose up -d
```

### 3. 啟動 FastAPI 服務
```bash
cd backend
CRON_JOB=true python -m uvicorn app.main:app --reload
```

### 4. 啟動 Kafka 消費者（如需要）
```bash
cd backend
python -m app.mq.consumer
```

## 測試
在專案根目錄執行：
```bash
pytest
```

## 更多資訊
- 詳細後端說明請參考 [backend/README.md](backend/README.md)
- 系統架構與功能需求請見 [PROJECT_SCOPE.md](PROJECT_SCOPE.md)

