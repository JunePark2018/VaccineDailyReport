from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User
import crud

# 1. 테스트용 임시 DB 생성 (메모리에서 동작하는 SQLite)
# MySQL 서버가 없어도 실행 가능합니다. 꺼지면 데이터는 사라집니다.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 2. DB 세션 생성기 만들기
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 테이블 만들기 (models.py에 정의된 User 테이블 생성)
Base.metadata.create_all(bind=engine)

def test():
    # DB 세션 열기
    db = SessionLocal()
    
    print("--- [테스트 시작] ---")

    # ==========================================
    # TEST 1: 사용자 생성 (Create)
    # ==========================================
    print("\n1. 사용자 생성 테스트 중...")
    user_data = {
        "login_id": "test_user_01",
        "password_hash": "secret1234",
        "user_real_name": "테스트계정",
        "email": "test@example.com",
        "subscribed_categories": ["경제", "사회"],
        "marketing_agree": True
    }
    
    created_user = crud.create_user(db, user_data)
    
    if created_user:
        print(f"✅ 생성 성공! ID: {created_user.login_id}, 이름: {created_user.user_real_name}")
    else:
        print("❌ 생성 실패")

    # ==========================================
    # TEST 2: 사용자 조회 (Read)
    # ==========================================
    print("\n2. 사용자 조회 테스트 중...")
    target_id = "test_user_01"
    fetched_user = crud.get_user(db, target_id)
    
    if fetched_user:
        print(f"✅ 조회 성공! 가져온 데이터: {fetched_user.email}")
        print(f"   구독 카테고리(JSON): {fetched_user.subscribed_categories}")
    else:
        print("❌ 조회 실패: 유저가 없습니다.")

    # ==========================================
    # TEST 3: 중복 가입 방지 테스트
    # ==========================================
    print("\n3. 중복 아이디 생성 테스트 (실패해야 정상)...")
    duplicate_user = crud.create_user(db, user_data) # 똑같은 데이터로 한 번 더 시도
    
    if duplicate_user is None:
        print("✅ 중복 방지 성공! (None이 반환됨)")
    else:
        print("❌ 중복 방지 실패 (생성되어 버림)")

    # DB 세션 닫기
    db.close()
    print("\n--- [테스트 종료] ---")

if __name__ == "__main__":
    test()