# syntax=docker/dockerfile:1

FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci || npm i
COPY . .
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV

RUN npm run build -- --mode production

# ---- Runtime ----
FROM nginx:alpine
WORKDIR /usr/share/nginx/html
COPY --from=build /app/public ./
COPY --from=build /app/dist ./dist
# 多加這行：把 dist/bundle.js 放到根目錄
COPY --from=build /app/dist/bundle.js ./bundle.js

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]