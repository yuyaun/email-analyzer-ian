# Feature: Kafka 任務處理與 GPT 呼叫流程建置

## 背景（Business Context）

為實現使用者非同步內容分析功能，系統需支援從 `/generate` 發送請求至 Kafka，再由 LLM Worker 處理並透過 LangChain 呼叫 GPT-4o Mini，最終將結果寫入 PostgreSQL。

## 使用者故事（User Story）

作為【開發者】

我希望在 /generate API 中推送任務至 Kafka

並由 Worker 使用 LangChain 呼叫 GPT 處理，結果寫入資料庫

以便實現穩定、可擴展的 AI 分析流程

## 驗收條件（Acceptance Criteria）

- [x] FastAPI 實作 `/api/public/v1/generate`，驗證 JWT 後推送任務至 Kafka
- [x] 建立 LLM Worker，可從 Kafka 消費任務並處理內容
- [x] Worker 使用 LangChain 封裝 prompt 並呼叫 GPT-4o Mini
- [x] GPT 回應結果為 JSON 格式（含標題優化、情感、是否垃圾訊息）
- [x] Worker 將處理結果寫入 PostgreSQL
- [x] Worker 支援一次處理多筆任務並平行運算後批次寫入
- [x] Worker 逐筆將結果以 `{task_id, results}` 結構發佈至 Kafka 結果 Topic，供 API 端依 `task_id` 取得結果
- [x] 撰寫 backend 與 worker 的初版 Kubernetes YAML 檔案

## 輸入資料（Inputs）

### /generate 請求範例

一次送入多筆任務，以陣列方式傳遞：

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

`num_suggestions` 用來指定要向 GPT 產生多少筆建議，數值越大則會呼叫 GPT 多次。

### JWT 驗證格式（Authorization Header）

```
Authorization: Bearer <your-jwt-token>
```

### GPT 回應格式範例

```json
{
  "title": "買一送一限時優惠，快邀好友一起搶購！",
  "sentiment": "positive",
  "is_spam": false
}
```

### Kafka 結果回傳格式

Worker 會將每個任務的處理結果逐筆發佈至 `Kafka` 的結果 Topic，訊息結構如下：

```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "results": [
    {
      "title": "買一送一限時優惠，快邀好友一起搶購！",
      "sentiment": "positive",
      "is_spam": false
    }
  ]
}
```

`task_id` 用於 API 端對應原始請求，`results` 為 LLM 產出的內容陣列。

---

若未來你要加入多種 `magicType` 對應不同的 LangChain Chain，可以擴充 `Worker` 的處理邏輯。是否需要也列為延伸功能？

## 延伸功能（Future Enhancements）

### 🎯 支援多種 `magicType` 對應不同的 LLM Chain 任務

為滿足更多 AI 處理需求，系統將擴充不同 `magicType` 類型的處理能力，例如標題優化、情感分析、垃圾郵件判斷等，並透過模組化設計拆分對應的 LangChain Chain。

### 範例 magicType 對應表

| magicType          | 功能描述                | 對應 Chain 函式              |
| ------------------ | ----------------------- | ---------------------------- |
| `title_optimize`   | 優化標題文案            | `get_title_optimize_chain()` |
| `sentiment_detect` | 分析內容情緒傾向        | `get_sentiment_chain()`      |
| `spam_check`       | 判斷是否為垃圾訊息      | `get_spam_check_chain()`     |
| `sku_mapping`      | 商品描述對應 SKU（RAG） | `get_rag_chain_to_sku()`     |

### Chain 設計原則

- 每個 `magicType` 對應一個專屬的 LangChain Chain
- Chain 輸入統一為：`{"content": str, ...}`
- 輸出皆為結構化 JSON，方便入庫
- 可透過 `magicType -> chain_map` 的方式切換調用

### 範例 chain_map 撰寫方式

```python
chain_map = {
    "title_optimize": get_title_optimize_chain(),
    "sentiment_detect": get_sentiment_chain(),
    "spam_check": get_spam_check_chain(),
    "sku_mapping": get_rag_chain_to_sku()
}

selected_chain = chain_map[data["magicType"]]
result = selected_chain.invoke({"content": data["content"]})
```

## 🧩 Kubernetes ConfigMap（環境參數設定）

```yaml
# k8s/llm-worker-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: llm-worker-config
  namespace: your-namespace
data:
  KAFKA_BOOTSTRAP_SERVERS: kafka:9092
  KAFKA_TOPIC: magic-task
  POSTGRES_URL: postgresql://user:password@pg:5432/yourdb
  OPENAI_API_KEY: sk-xxx
  OPENAI_MODEL: gpt-4o-mini
```

---

## 🚀 Kubernetes Deployment

```yaml
# k8s/llm-worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-worker
  namespace: your-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: llm-worker
  template:
    metadata:
      labels:
        app: llm-worker
    spec:
      containers:
        - name: llm-worker
          image: your-registry/llm-worker:latest
          imagePullPolicy: Always
          envFrom:
            - configMapRef:
                name: llm-worker-config
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1"
              memory: "1Gi"
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
```

---

## 📄 ConfigMap + YAML 設計原則摘要

| 類型         | 說明                                                            |
| ------------ | --------------------------------------------------------------- |
| `ConfigMap`  | 集中管理 Kafka、PostgreSQL、OpenAI 金鑰與模型名稱等參數         |
| `Deployment` | 啟動 worker 容器，從 Kafka 消費並使用 LangChain 處理            |
| `Probe`      | 建議提供 `/healthz` endpoint 讓 K8s 監測健康狀態，避免 Pod 卡死 |
| `envFrom`    | 使用 ConfigMap 簡化環境變數注入                                 |
| `resources`  | 初步設置適度資源，避免佔用整個節點，可後續依 GPT latency 調整   |

---

若你使用 **Secret** 儲存 API Key，可以將 `OPENAI_API_KEY` 移到 Secret，再透過 `envFrom: secretRef` 注入。
