"""
사용자 관련 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from routers import get_db
from database.crud import (
    create_user,
    get_user_by_login_id,
    update_user_subscriptions,
    add_view,
    bump_user_keyword_stats_from_ai_news,
    list_user_top_keywords,
    clear_user_keyword_stats,
    delete_user_account,
    get_ai_generated_news,
    get_category_name,
    get_reaction,
)
from schemas import UserCreateRequest, UserLoginRequest, UserUpdate, UserDashboardResponse

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
        "user_id": new_user.user_id,
        "login_id": new_user.login_id,
        "user_real_name": new_user.user_real_name,
        "email": new_user.email,
        "user_status": new_user.user_status,
        "created_at": new_user.created_at,
        "subscribed_categories": [cat.name for cat in new_user.subscribed_categories],
        "subscribed_keywords": [kw.keyword for kw in new_user.keyword_subscriptions],
    }


@router.delete("/{login_id}/keywords/stats")
def clear_interest_keywords(login_id: str, db: Session = Depends(get_db)):
    """
    사용자의 모든 관심 키워드 통계 초기화
    """
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    deleted_count = clear_user_keyword_stats(db, user_id=user.user_id)
    db.commit()
    
    return {"message": "Keywords cleared", "deleted_count": deleted_count}


@router.delete("/{login_id}")
def delete_user_account_endpoint(login_id: str, db: Session = Depends(get_db)):
    """
    사용자 계정 완전 삭제 (회원탈퇴)
    모든 관련 데이터도 함께 삭제됩니다.
    """
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = delete_user_account(db, user_id=user.user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete account")
    
    db.commit()
    
    return {"message": "Account deleted successfully"}


@router.get("/{login_id}/reactions/{news_id}")
def get_user_reaction(login_id: str, news_id: int, db: Session = Depends(get_db)):
    """
    사용자의 특정 기사에 대한 좋아요/싫어요 상태 조회
    Returns: {"value": 1 or -1 or null}
    """
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reaction_value = get_reaction(db, user_id=user.user_id, ai_news_id=news_id)
    
    return {"value": reaction_value}


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
        "user_id": user.user_id,
        "login_id": user.login_id,
        "user_real_name": user.user_real_name,
        "email": user.email,
        "age_range": user.age_range,
        "gender": user.gender,
        "marketing_agree": user.marketing_agree,
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
        try:
            update_user_subscriptions(db, user, user_update.subscribed_categories, user_update.subscribed_keywords)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="DB 업데이트 실패")

    return {"message": f"'{login_id}'님의 정보가 수정되었습니다."}


@router.post("/{login_id}/read/{news_id}")
def record_article_read(login_id: str, news_id: int, db: Session = Depends(get_db)):
    """
    기사 읽음 처리:
    1. NewsView에 기록 (중복이면 시간 갱신)
    2. ai_generated_news에서 키워드 추출하여 UserKeywordReadStat 업데이트
    """
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. View 기록
    # unique_per_user=True: 같은 기사를 여러 번 봐도 카운트는 1번만 오르거나, viewed_at만 갱신
    # 여기서는 "읽은 이력" 자체를 남기는 게 중요하므로 add_view 호출
    add_view(db, user_id=user.user_id, ai_news_id=news_id, unique_per_user=True)

    # 2. 키워드 가중치 업데이트
    # 기사 정보를 가져와서 키워드가 있다면 +1
    # 이미 본 기사라도 다시 읽으면 관심도가 올라간다고 가정할 수 있음.
    # 단, 너무 루프 도는 것을 방지하려면 has_viewed 체크를 할 수도 있으나,
    # 여기서는 "읽을 때마다 관심도 증가"로 구현.
    bump_user_keyword_stats_from_ai_news(db, user_id=user.user_id, ai_news_id=news_id, inc=1)

    db.commit()
    return {"message": "Read recorded"}


@router.get("/{login_id}/dashboard", response_model=UserDashboardResponse)

def get_user_dashboard(login_id: str, db: Session = Depends(get_db)):
    """
    마이페이지 대시보드 데이터 조회
    """
    user = get_user_by_login_id(db, login_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. Top Interest Keywords (상위 10개)
    # crud.list_user_top_keywords returns [(keyword, count), ...]
    top_kws_list = list_user_top_keywords(db, user_id=user.user_id, limit=1000)
    # 딕셔너리로 변환
    read_keywords_map = {kw: count for kw, count in top_kws_list}

    # 2. Category Read Counts
    # user.views (NewsView)를 통해 집계
    # NewsView에는 category_id가 저장되어 있지 않을 수도 있음(초기 설계 상).
    # 하지만 AiGeneratedNews join해서 카운트 가능
    # 여기서는 간단히 user.views -> news -> category로 접근하거나
    # NewsView에 category_id가 있다면 그것을 씀 (models.py에 category_id 있음)
    from sqlalchemy import func
    from database.models import NewsView

    # 카테고리별 읽은 횟수 집계
    cat_counts = (
        db.query(NewsView.category_id, func.count(NewsView.news_view_id))
        .filter(NewsView.user_id == user.user_id)
        .group_by(NewsView.category_id)
        .all()
    )

    read_categories_map = {}
    for cat_id, count in cat_counts:
        if cat_id:
            c_name = get_category_name(db, cat_id)
            if c_name:
                read_categories_map[c_name] = count
        else:
            # 카테고리가 없는 경우 (미분류 등)
            pass

    # 3. Subscribed Keywords
    sub_kws = [k.keyword for k in user.keyword_subscriptions]

    return UserDashboardResponse(
        user_real_name=user.user_real_name,
        email=user.email,
        read_categories=read_categories_map,
        read_keywords=read_keywords_map,
        subscribed_keywords=sub_kws,
    )
