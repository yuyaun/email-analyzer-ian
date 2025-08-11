# Feature: 魔法建議產生機制與輸入驗證

## 背景（Business Context）

為了提升郵件內容的行銷成效，提供使用者 AI 驅動的標題與預覽文字建議。系統需支援前端輸入驗證與後端結果展示，確保體驗順暢且符合預期。

## 使用者故事（User Story）

作為【行銷使用者】

我希望在輸入足夠內容後點選「用魔法打敗魔法」產生建議結果

以便快速獲得吸引人的標題與預覽文字

## 驗收條件（Acceptance Criteria）

- [x] 若輸入的「想要幾個點子」大於 3，則：
  - 不送出 API 請求
  - 顯示錯誤提示：`最多只能選 3 個點子唷！`
- [x] 若輸入的「郵件內容」少於 50 字，則：
  - 不送出 API 請求
  - 顯示錯誤提示：`字太少囉！至少給 50 個字才能發揮魔法～`
- [x] 當按下「用魔法打敗魔法」並成功取得回應後，顯示區塊「✨ 魔法建議結果：」
  - `magic_type = title_optimize` 每一筆建議結果顯示：
    - 標題：`title`
    - 預覽文字：`preheader`

## 輸入資料（Inputs）

### API 請求欄位

```json
{
  "campaignSn": "string",
  "magic_type": "title_optimize",
  "content": "string",
  "count": 1
}
```

## 輸出資料（Outputs）

### 成功範例回傳（`magic_type = title_optimize`）

```json
{
  "magic_type": "title_optimize",
  "status": "done",
  "result": [{ "title": "string", "preheader": "string" }]
}
```
