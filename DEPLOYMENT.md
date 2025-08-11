# Kubernetes Deployment Guide

本文件說明如何在 Kubernetes 叢集中部署 Email Analyzer。透過 `kubectl` 套用 `k8s/` 目錄提供的 YAML 清單即可完成部署。

## 先決條件

- 已安裝 `kubectl` 並連線至目標叢集。
- 可以存取 Docker 映像倉庫，並替換清單中的 `<REG>` 與 `<TAG>` 等占位符。
- 在 `k8s/llm-worker-secret.yaml` 中填入有效的 `OPENAI_API_KEY` 與資料庫連線字串。

## 部署步驟

1. **建置並推送後端映像**

   在部署前先從 `backend/` 目錄建置 Docker 映像並推送至你的映像倉庫，並同步更新 `k8s/apps/backend/deployment.yaml` 中的 `<REG>` 與 `<TAG>`。

   ```bash
   docker build -t <REG>/backend:<TAG> backend/
   docker push <REG>/backend:<TAG>
   # 更新既有部署時可使用
   kubectl -n <namespace> set image deployment/backend backend=<REG>/backend:<TAG>
   ```

2. **建立命名空間與基礎服務**

   ```bash
   kubectl apply -f k8s/base/namespace.yaml
   kubectl apply -f k8s/base/postgres/
   kubectl apply -f k8s/base/kafka/
   kubectl apply -f k8s/base/ingress.yaml
   ```

3. **部署後端與前端應用**

   ```bash
   kubectl apply -f k8s/apps/backend/
   kubectl apply -f k8s/apps/frontend/
   ```

4. **部署 LLM Worker**

   ```bash
   kubectl apply -f k8s/llm-worker-config.yaml
   kubectl apply -f k8s/llm-worker-secret.yaml
   kubectl apply -f k8s/llm-worker-deployment.yaml
   ```

5. **確認服務狀態**

   ```bash
   kubectl get pods -n <namespace>
   kubectl get svc  -n <namespace>
   ```

## 自訂設定

- 修改各 `configmap.yaml` 或 `secret.yaml` 以調整環境變數、憑證等設定。
- 可在 `deployment.yaml` 中調整 `replicas` 與 `resources` 以符合資源需求。
- 若需自訂網域，請更新 `k8s/base/ingress.yaml` 中的 `host` 設定。

