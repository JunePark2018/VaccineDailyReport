"""
사용자 관련 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from routers import get_db
from database.crud import create_user, get_user, get_user_by_login_id, update_user_subscriptions
from schemas import UserCreateRequest, UserLoginRequest, UserUpdate  # UserResponse 제거

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("")  # response_model 제거
def signup(user: UserCreateRequest, db: Session = Depends(get_db)):
    """
    새 사용자 정보로 회원가입을 합니다. (중복 아이디 체크 포함)
    """
    existing_user = get_user_by_login_id(db, user.login_id)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 아이디입니다.")

    new_user = create_user(
        db,
        login_id=user.login_id,
        user_real_name=user.user_real_name,
        password_hash=user.password_hash,
        email=user.email,
        subscribed_categories=user.subscribed_categories,
        subscribed_keywords=user.subscribed_keywords,
    )
    # create_user 내부에서 commit/refresh 하므로 id확보됨

    # 응답 포맷 구성
    return {
        "id": new_user.id,
        "login_id": new_user.login_id,
        "user_real_name": new_user.user_real_name,
        "email": new_user.email,
        "user_status": new_user.user_status,
        "created_at": new_user.created_at,
        "subscribed_categories": [cat.name for cat in new_user.subscribed_categories],
        "subscribed_keywords": [kw.keyword for kw in new_user.keyword_subscriptions],
    }


@router.get("/{login_id}")  # response_model 제거
def read_user(login_id: str, db: Session = Depends(get_db)):
    """
    특정 사용자 ID의 정보를 가져옵니다.
    """
    user = get_user_by_login_id(db, login_id)

    if user is None:
        raise HTTPException(status_code=404, detail="해당 아이디의 유저를 찾을 수 없습니다.")

    subscribed_categories = [cat.name for cat in user.subscribed_categories]
    subscribed_keywords = [kw.keyword for kw in user.keyword_subscriptions]

    return {
        "id": user.id,
        "login_id": user.login_id,
        "user_real_name": user.user_real_name,
        "email": user.email,
        # phone_number 제거 - 스키마에 없음
        "subscribed_categories": subscribed_categories,
        "subscribed_keywords": subscribed_keywords,
    }


@router.put("/{login_id}")
def update_user(login_id: str, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    사용자 정보 업데이트
    """
    user = get_user_by_login_id(db, login_id)

    if not user:
        raise HTTPException(status_code=404, detail="해당 아이디의 유저를 찾을 수 없습니다.")

    update_data = user_update.dict(exclude_unset=True)
    excluded_fields = {"subscribed_categories", "subscribed_keywords"}

    for key, value in update_data.items():
        if key in excluded_fields:
            continue
        elif key == "password":
            user.password_hash = value
        else:
            setattr(user, key, value)

    if user_update.subscribed_categories is not None or user_update.subscribed_keywords is not None:
        update_user_subscriptions(db, user, user_update.subscribed_categories, user_update.subscribed_keywords)

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="DB 업데이트 실패")

    return {"message": f"'{login_id}'님의 정보가 수정되었습니다."}
