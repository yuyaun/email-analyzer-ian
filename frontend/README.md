# 📬 FrontendAgent - Email Optimizer

這是一個使用 Vue 3 + Webpack + Tailwind 打造的 AI 郵件優化工具，支援上傳郵件內容，並搭配 AI 分析郵件標題、預覽文字、情感語氣與垃圾郵件風險等功能。

## ✨ 功能特色

- 上傳 `.txt` / `.html` 郵件內容（限制 1MB）
- 可輸入郵件內容，選擇「魔法類型」進行優化建議
- 具備冷卻倒數（防止暴力連點）
- 自動產生 JWT 串接後端 API (`/jwt`, `/generate`)
- 支援多種郵件優化模式（標題、預覽、情感分析、風險檢測等）
- 防止內容未變更重複送出
- 可處理伺服器 429 次數過多錯誤

## 🛠️ 安裝與啟動

```bash
# 安裝依賴
npm install

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
│   ├── components/
│   │   └── EmailMagicForm.vue  # 主表單元件
│   └── utils/
│       └── jwt.js           # JWT 產生工具
├── tailwind.config.js
├── postcss.config.js
├── webpack.config.js
├── package.json
└── README.md
```

## 📦 對接 API

### /jwt

- 說明：前端首次點擊「用魔法打敗魔法」時，會根據 `userSn` 與 `exp` 組成 JWT，並儲存於記憶體中。
- 格式：

```json
{
  "userSn": "dev-fe-1690000000",
  "exp": 1690001200
}
```

### /generate

- 說明：後續請求皆會帶上 JWT 作為 Bearer Token 串接 API。
- Request Body:

```json
{
  "campaignSn": "字串識別碼",
  "content": "郵件內容",
  "generation_type": "title | preview | spam | ...",
  "num_suggestions": 2 // 可選，僅部分類型需要
}
```

- Response 範例：依據不同 `generation_type`，會有不同格式。

### 錯誤處理（429）

```json
{
  "message": "請求過於頻繁",
  "nextAllowedTime": "2023-10-01T12:00:00Z"
}
```
