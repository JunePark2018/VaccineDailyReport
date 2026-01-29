# 1단계: 빌드 스테이지
FROM node:18-alpine AS builder
WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install

# 소스 복사
COPY . .

# [중요] docker-compose의 args로부터 IP 주소를 받아옴
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# 이 시점에 NEXT_PUBLIC_API_URL이 정적 파일에 포함됨
RUN npm run build

# 2단계: 실행 스테이지 (Nginx)
FROM nginx:stable-alpine
COPY --from=builder /app/build /usr/share/nginx/html

# React 라우팅 대응 Nginx 설정
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
