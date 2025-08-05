# Feature: 專案初始化與 JWT 驗證機制

## 背景（Business Context）

為後續開發打好基礎，需完成專案初始化，包含資料夾結構、驗證機制、本地測試環境與前端雛型。

## 使用者故事（User Story）

作為【開發者】  
我希望專案具備基本驗證與本地環境  
以便快速開始功能開發與測試

## 驗收條件（Acceptance Criteria）

- [ ] 建立 Git 專案與目錄結構（backend、frontend、k8s）
- [ ] FastAPI 實作 `/jwt`，回傳 JWT token
- [ ] docker-compose `/backend/docker-compose.yaml` 啟動 PostgreSQL 與 Kafka
- [ ] backend Dockerfile `/backend/Dockerfile.dev` 可正常 build 與執行
- [ ] frontend `frontend`初版 Vue 頁面可顯示並串接後端

## 輸入資料（Inputs）

### JWT 請求範例

```json
{
  "userSn": "string", // ({env}-{role}-{exp})
  "exp": "string" // (now + 20m)
}
```
