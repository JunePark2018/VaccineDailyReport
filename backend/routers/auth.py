"""
로그인 관련 라우터
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from routers import get_db
from database.crud import get_user_by_login_id
from schemas import UserLoginRequest

router = APIRouter(tags=["Users"])


@router.post("/login")
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """
    로그인을 합니다. ID나 비밀번호가 맞는지 비교하며, 응답문은 JSON 형태입니다.
    JSON의 success 항목이 True면 로그인에 성공한 것입니다.
    """
    user = get_user_by_login_id(db, request.login_id)

    if not user or user.password_hash != request.password:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다.")

    return {
        "success": True,
        "message": "로그인에 성공하였습니다!",
        "user_id": user.user_id,
        "login_id": user.login_id,
        "user_real_name": user.user_real_name,
    }
