# 1. 파이썬 3.11 슬림 버전 사용
FROM python:3.11-slim

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# [추가] ARM 환경에서 hdbscan 등 C 기반 라이브러리 빌드를 위한 필수 도구
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. 필요한 라이브러리 설치
COPY requirements.txt .
# [추가] Cython을 먼저 깔아주면 hdbscan 빌드 성공 확률이 비약적으로 높아집니다
RUN pip install --no-cache-dir Cython && \
    pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 전체 복사
COPY . .

# 5. FastAPI 실행 (포트 8000번 사용)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
