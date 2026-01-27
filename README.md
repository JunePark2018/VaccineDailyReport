# 💉 VaccineDailyReport
### 하이미디어 1조 AI 웹앱 프로젝트

> 📝 **프로젝트 설명**
>
> 원래 여기에 프로젝트 설명이 들어갑니다.<br>
> 마크다운 문법으로 수정 가능합니다. 문법은 구글링하거나 AI에게 물어보시면 쉽게 알 수 있습니당

## 🚀 시작하기

### 1. 리포지토리 복제

```bash
# 터미널에서 아래 명령어로 프로젝트를 다운로드하세요
git clone https://github.com/JunePark2018/VaccineDailyReport.git

```

### 2. 데이터베이스 설정
이 프로젝트는 **PostgreSQL**과 **Redis**를 Docker 컨테이너로 실행합니다. 팀원 모두가 동일한 DB 환경에서 작업하기 위해 사용합니다.

1.  **Docker Desktop 설치**: Docker가 설치되어 있고 실행 중이어야 합니다.
    *   https://hub.docker.com/에 접속하여 로그인하신 후, 프로그램을 다운받아 주세요.
2.  **.env 파일 수정**: 아래 코드를 .env에 붙여넣으세요.
    ```bash
    DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/finalproject
    REDIS_URL=redis://localhost:6379/0
    ```
3.  **서비스 실행**: 프로젝트 루트 폴더에서 아래 명령어를 실행하세요.
    ```bash
    docker-compose up -d
    ```
    *   **Postgres**: 5432 포트
    *   **Redis**: 6379 포트
    *   **Adminer** (DB 관리 도구): http://localhost:8080
4.  **DB 열람**: 도커 내 Adminer를 활용하시면 됩니다.
    🌐 Adminer 접속 방법
    1. 웹 브라우저를 켭니다.
    2. 주소창에 http://localhost:8080 을 입력합니다.
    3. 로그인 화면에서 아래 정보를 입력하세요:
       * System: PostgreSQL (셀렉트 박스에서 선택)
       * Server: postgres
       * Username: myuser
       * Password: mypassword
       * Database: finalproject
    로그인하시면 테이블 목록과 저장된 데이터를 엑셀처럼 보거나 SQL 쿼리를 직접 날리실 수 있습니다.
5.  **데이터 보존**: DB 데이터는 프로젝트 폴더 내 `./postgres_data` 에 저장되므로, 컨테이너를 꺼도 데이터가 유지됩니다.

#### ⚠️ DB 초기화 (데이터 삭제)
DB를 완전히 삭제하고 처음부터 다시 시작하려면 다음 과정을 따르세요.
1.  컨테이너 종료: `docker-compose down`
2.  폴더 삭제: `./postgres_data` 폴더를 삭제
3.  서비스 재실행: `docker-compose up -d`

### 3. 백엔드 설정
1.  **가상환경 및 의존성 설치**:
    ```bash
    # 가상환경 생성 (선택 사항)
    python -m venv venv
    
    # 의존성 설치
    pip install -r backend/requirements.txt
    ```
2.  **환경 변수 설정**: `.env` 파일이 있는지 확인하세요. (없다면 팀원에게 요청)
3.  **서버 실행**:
    ```bash
    cd backend
    uvicorn main:app --reload
    ```

### 4. 프론트엔드 설정
1.  **의존성 설치**:
    ```bash
    # 프론트엔드 폴더 이동
    cd frontend

    # 의존성 설치
    npm i
    ```
2.  **서버 실행**
    ```bash
    npm start
    ```


## 🤝 쓰실 때
* 로컬에서 `git add`, `git commit`을 활용해 자유롭게 개발하시면 됩니다.
* **⚠️ `git push`를 하기 전, 반드시 본인의 브랜치(Branch)인지 확인해 주세요!** `main` 브랜치에 직접 푸시하지 않도록 주의 바랍니다.
* 나중에 `Pull Requests` 탭에서 함께 push된 코드를 확인하며 병합을 진행하고자 합니다.

## 기타
* 기존 로컬 프로젝트에서 github에 있는 최신 프로젝트로 업데이트할 때, `git pull`을 쓰면 최신 파일을 가져오기는 하지만 로컬 파일의 변경사항도 그대로 유지됩니다. 만약 **로컬을 날리고 최신 프로젝트로 완전히 초기화**하고 싶으시다면 아래 명령어를 쓰면 됩니다.
```diff
- 주의: 이 명령어를 실행하면 로컬의 모든 데이터가 삭제됩니다.
```
```bash
# 1. 먼저 메인 브랜치로 이동합니다. (가장 중요!)
git checkout main

# 2. 원격 저장소의 최신 정보를 가져옵니다.
git fetch --all

# 3. 로컬의 상태를 원격 main과 100% 동일하게 강제 초기화합니다.
git reset --hard origin/main

# 4. 추적되지 않는 찌꺼기 파일(새로 생긴 파일 등)을 삭제합니다.
git clean -fd

# 5. main을 제외한 모든 브랜치 삭제
git branch | grep -v "main" | xargs git branch -D

# 6. 위 명령어가 오류가 날 경우를 대비한 명령어
git branch --format "%(refname:short)" | ? { $_ -ne "main" } | % { git branch -D $_ }
```

