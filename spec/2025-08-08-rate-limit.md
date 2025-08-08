# Feature: `/generate` API Rate Limit 與錯誤提示機制

## 背景（Business Context）

為避免濫用或不當使用 `/generate` API，造成系統負載過高或服務品質下降，需要實施請求頻率限制（Rate Limiting）機制，並於超出限制時提供清楚的錯誤提示。

## 使用者故事（User Story）

作為【後端開發者】

我希望能限制 `/generate` API 的請求頻率

以保障系統資源並提升整體穩定性與可維運性

## 驗收條件（Acceptance Criteria）

- [ ]  為 `/generate` API 增加速率限制（每個 IP、每個 JWT 使用者皆可限制）
- [ ]  若請求超出限制，回傳 HTTP 狀態碼 `429 Too Many Requests`
- [ ]  回應內容需包含錯誤訊息，例如：`"Too many requests, please try again later."`
- [ ]  可透過 FastAPI 的中介層（middleware）或 Starlette 的 `Limiter` 實作
- [ ]  支援設定速率限制參數，例如：每個 IP 每分鐘最多 10 次請求（可參數化）

## 技術實作（Technical Implementation）

- 使用 `slowapi` 或 `fastapi-limiter` 套件實現 rate limit 機制
- 設定 Redis 作為限流狀態儲存的 backend
- 於 `/generate` API 上新增裝飾器限制流量
- 加入自定義 exception handler 處理 `429` 錯誤回應格式

### 

### 應用在 `/generate` API 上

```python
from slowapi.decorator import limiter

@app.post("/api/public/v1/generate")
@limiter.limit("10/minute")
async def generate_task(...):
    ...
```

### 自定義錯誤訊息（可選）

```python
@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"message": "Too many requests, please try again later."}
    )
```

## 延伸功能（Future Enhancements）

### 🎯 根據 JWT Token 區分使用者流量限制

透過 JWT payload 中的 `userSn` 或 `email` 欄位，實作 per-user 的速率限制邏輯，提升客製化程度與風險控管能力。

### 🎯 限制非同步任務數量（排隊控制）

- 除了速率限制外，亦可實作排隊長度限制（任務佇列過長即拒絕新任務）
- 當 memory store 或 Kafka backlog 超過閾值時，回傳 `503 Service Unavailable`
