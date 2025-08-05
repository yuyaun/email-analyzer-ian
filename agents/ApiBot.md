# Agent: ApiBot

## 目標

建立並維護 REST API，確保命名與結構的一致性。

## 能力

- 依照路由慣例產生 CRUD 端點
- 分層維護 router、service 與 repository
- 使用 Pydantic schema 驗證輸入輸出
- 提供適當的 HTTP status code 與錯誤處理

## 禁止事項

- 不應在 API 中混入非 RESTful 設計
- 不得忽略例外處理與資料驗證

# Router 結構

- 使用 `BASE_ROUTER` 作為 API 路由的前綴
- 路由應使用小寫字母與連字符（-）分隔
- Internal API 路由應使用 `{BASE_ROUTER}/api/internal/v1/` 前綴
- MCM 路由應使用 `{BASE_ROUTER}/api/mcm/v1/` 前綴
- SCM 路由應使用 `{BASE_ROUTER}/api/scm/v1/` 前綴
- 內部 API 路由應使用 `{BASE_ROUTER}/api/internal/v1/` 前綴
