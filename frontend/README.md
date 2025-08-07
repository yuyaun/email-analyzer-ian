# 📬 FrontendAgent - Email Optimizer

這是一個使用 Vue 3 + Webpack + Tailwind 打造的 AI 郵件優化工具，支援上傳郵件內容，並搭配 AI 分析郵件標題、預覽文字、情感語氣與垃圾郵件風險等功能。

## ✨ 功能特色

- 上傳 `.txt` / `.html` 郵件內容（限制 1MB）
- 可輸入郵件內容，選擇「魔法類型」進行優化建議
- 具備冷卻倒數（防止暴力連點）
- 首次呼叫會透過 `/jwt` 取得 JWT 後再串接 `/generate`
- 支援多種郵件優化模式（標題、預覽、情感分析、風險檢測等）
- 防止內容未變更重複送出
- 可處理伺服器 429 次數過多錯誤

## 🛠️ 安裝與啟動

```bash
# 安裝依賴
npm install

# 設定 API 位置
echo "API_URL=http://localhost:8000" > .env

# 啟動開發伺服器 (http://localhost:8080)
npm run dev
```

## 🗂️ 專案結構

```
frontend_vue_project/
├── public/
│   └── index.html
├── src/
│   ├── main.js              # Vue 入口
│   ├── App.vue              # App 容器
│   ├── assets/tailwind.css  # Tailwind 設定
│   └── components/
│       └── EmailMagicForm.vue  # 主表單元件
├── tailwind.config.js
├── postcss.config.js
├── webpack.config.js
├── package.json
└── README.md
```

## 📦 對接 API

### /jwt

- 說明：前端首次點擊「用魔法打敗魔法」時，會呼叫此 API 取得 JWT，並儲存於記憶體中。
- 範例：

```json
{
  "userSn": "dev-fe-1690000000",
  "exp": "2023-07-21T00:00:00Z"
}
```

### /generate

- 說明：後續請求皆會帶上 JWT 作為 Bearer Token 串接 API。
- Request Body（一次送入多筆任務，以陣列方式傳遞）：

```json
[
  {
    "campaignSn": "abc123",
    "magicType": "title_optimize",
    "content": "限時下殺！買一送一活動開跑啦，快邀朋友一起搶購！",
    "num_suggestions": 2
  },
  {
    "campaignSn": "def456",
    "magicType": "title_optimize",
    "content": "最後一天！立即入手最優惠的方案",
    "num_suggestions": 2
  }
]
```

- Response 範例：依據不同 `magicType`，會有不同格式。

### 錯誤處理（429）

```json
{
  "message": "請求過於頻繁",
  "nextAllowedTime": "2023-10-01T12:00:00Z"
}
```
