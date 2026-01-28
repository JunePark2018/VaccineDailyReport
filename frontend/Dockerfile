# --- 스테이지 1: 빌드 ---
FROM node:18-alpine AS builder
WORKDIR /app

# 의존성 설치
COPY package*.json ./
RUN npm install

# 환경 변수 설정 (Build 시점에 필요)
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# 소스 복사 및 빌드
COPY . .
RUN npm run build

# --- 스테이지 2: 실행 (Nginx) ---
FROM nginx:stable-alpine

# 빌드 결과물(out 또는 .next)을 Nginx 웹 디렉토리로 복사
# Next.js export 모드인 경우 'out' 폴더를 복사합니다.
COPY --from=builder /app/out /usr/share/nginx/html

# Nginx 포트 개방
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]