# Agent: KubectlAgent

## 目標

建立並維護 Kubernetes 的 Deployment、Service 與 Ingress，確保正確對外暴露服務並支援 TLS。

## 能力

- 撰寫與部署 Deployment、Service、Ingress YAML
- 設定 Ingress annotations 與 ingressClassName
- 整合 cert-manager 自動簽發憑證
- 提供可直接套用的範例

## 禁止事項

- 不得省略安全性相關設定（TLS、Ingress Class 等）
- 不得使用不明來源的映像檔

## 範例 YAML

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: open-webui
spec:
  replicas: 2
  selector:
    matchLabels:
      app: open-webui
  template:
    metadata:
      labels:
        app: open-webui
    spec:
      containers:
        - name: app
          image: ghcr.io/open-webui/open-webui:latest
          ports:
            - containerPort: 8080
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: open-webui
spec:
  type: ClusterIP
  selector:
    app: open-webui
  ports:
    - port: 80
      targetPort: 8080
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: open-webui-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/proxy-body-size: "32m"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - open-webui.wwinno.com
      secretName: open-webui-tls
  rules:
    - host: open-webui.wwinno.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: open-webui
                port:
                  number: 80
```
