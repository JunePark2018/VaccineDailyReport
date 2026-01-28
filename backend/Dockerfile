# 1. 파이썬 3.11 슬림 버전 사용 (가볍고 빠름)
FROM python:3.11-slim

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3. 필요한 라이브러리 설치 (캐싱 활용을 위해 requirements 먼저 복사)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. 소스 코드 전체 복사
COPY . .

# 5. FastAPI 실행 (포트 8000번 사용)
# --host 0.0.0.0은 필수입니다!
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]