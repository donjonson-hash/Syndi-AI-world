# ============================================================
# frontend/Dockerfile — React + Vite + TypeScript + Tailwind
# Multi-stage: builder → production (nginx)
# ============================================================

# ---- Stage 1: Build ----------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Копируем package файлы первыми (кэш слоёв)
COPY package.json package-lock.json ./

# Устанавливаем зависимости строго по lock-файлу
RUN npm ci --frozen-lockfile

# Копируем исходный код
COPY . .

# Сборка production bundle
# VITE_API_URL передаётся через --build-arg или .env
ARG VITE_API_URL=http://localhost:8000
ARG VITE_WS_URL=ws://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_WS_URL=$VITE_WS_URL

RUN npm run build

# ---- Stage 2: Production (nginx) ---------------------------
FROM nginx:1.27-alpine AS production

# Копируем собранные файлы из builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx конфиг для React SPA (все роуты → index.html)
RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 3000;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Кэширование статики
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2|woff|ttf)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback — все пути на index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Healthcheck endpoint
    location /health {
        return 200 'ok';
        add_header Content-Type text/plain;
    }

    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript;
}
EOF

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:3000/health || exit 1

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]

# ============================================================
# Локальная разработка (без Docker):
#   cd frontend && npm install && npm run dev
#
# Сборка образа с кастомным API URL:
#   docker build \
#     --build-arg VITE_API_URL=https://api.syndi.ai \
#     -t syndi-frontend .
#
# Запуск:
#   docker run -p 3000:3000 syndi-frontend
# ============================================================
