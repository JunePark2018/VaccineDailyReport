# 💉 VaccineDailyReport
### 하이미디어 1조 AI 웹앱 프로젝트

> 📝 **프로젝트 설명**
>
> 원래 여기에 프로젝트 설명이 들어갑니다.<br>
> 마크다운 문법으로 수정 가능합니다. 문법은 구글링하거나 AI에게 물어보시면 쉽게 알 수 있습니당

## 🚀 시작하기

```bash
# 터미널에서 아래 명령어로 프로젝트를 다운로드하세요
git clone https://github.com/JunePark2018/VaccineDailyReport.git

```

## 🤝 쓰실 때
* 만약 `git clone` 대신 `git init`을 하셨다면, 브랜치를 만들기 전에 `git pull origin main`으로 pull을 하여 동기화를 먼저 진행해 주세요.
* 
* 로컬에서 `git add`, `git commit`을 활용해 자유롭게 개발하시면 됩니다.
* **⚠️ `git push`를 하기 전, 반드시 본인의 브랜치(Branch)인지 확인해 주세요!** `main` 브랜치에 직접 푸시하지 않도록 주의 바랍니다.
* 매일 **아침 회의 시간**에 `Pull Requests` 탭에서 함께 코드를 확인하며 병합을 진행하고자 합니다.

## 기타
* 기존 로컬 프로젝트에서 github에 있는 최신 프로젝트로 업데이트할 때, `git pull`을 쓰면 최신 파일을 가져오기는 하지만 로컬 파일의 변경사항도 그대로 유지됩니다. 만약 **최신 프로젝트로 완전히 초기화**하고 싶으시다면 아래 명령어를 쓰면 됩니다.
```bash
# 1. 먼저 메인 브랜치로 이동합니다. (가장 중요!)
git checkout main

# 2. 원격 저장소의 최신 정보를 가져옵니다.
git fetch --all

# 3. 로컬의 상태를 원격 main과 100% 동일하게 강제 초기화합니다.
git reset --hard origin/main

# 4. 추적되지 않는 찌꺼기 파일(새로 생긴 파일 등)을 삭제합니다.
git clean -fd
```
