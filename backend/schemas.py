from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime


# --- [Pydantic Models] Frontend Data Definitions ---
class NewsResponse(BaseModel):
    """
    뉴스 기사 응답 스키마

    id: 기사 ID
    title: 기사 제목
    contents: 기사 내용 (옵션)
    img_urls: 기사 내 사진 URL 목록 (옵션)
    url: 기사 URL
    company_name: 언론사명 (Company 테이블의 name)
    created_at: 기사 발행 시각
    region: 'domestic' | 'global'
    """

    id: int
    title: Optional[str] = None
    contents: Optional[str] = None
    img_urls: Optional[List[str]] = None
    url: str
    company_name: Optional[str] = None  # 모델에서는 relation이지만, 응답엔 이름만 줘도 무방
    created_at: datetime
    region: str

    class Config:
        from_attributes = True


class AiGeneratedNewsResponse(BaseModel):
    """
    AI 생성 기사 응답 스키마

    id: 기사 ID
    title: 기사 제목
    contents: 기사 내용
    created_at: 기사 생성 시각
    analysis_result: AI 비교분석 (JSON)
    keywords: 키워드 (JSON)
    """

    id: int
    cluster_id: int
    title: Optional[str] = None
    contents: Optional[str] = None
    created_at: datetime
    analysis_result: Optional[Any]
    keywords: Optional[List[str]] = None

    # 반응/조회수 (옵션)
    like_count: int = 0
    dislike_count: int = 0

    class Config:
        from_attributes = True


# 회원가입 요청 시 받을 데이터
class UserCreateRequest(BaseModel):
    """
    회원가입 요청 시 받을 스키마

    login_id: 사용자 ID
    password_hash: 비밀번호 (해시 전/후 처리는 서비스 로직에 따름)
    user_real_name: 실명 (옵션)
    email: 이메일 (옵션)
    age_range: 연령대 (옵션)
    gender: 성별 (옵션)
    subscribed_categories: 구독한 카테고리 이름 목록 (옵션)
    subscribed_keywords: 구독한 키워드 텍스트 목록 (옵션)
    marketing_agree: 마케팅 동의
    """

    login_id: str
    password_hash: str
    user_real_name: Optional[str] = None
    email: Optional[str] = None
    age_range: Optional[str] = None
    gender: Optional[str] = None
    subscribed_categories: Optional[List[str]] = []
    subscribed_keywords: Optional[List[str]] = []
    marketing_agree: bool = False


# 클라이언트에게 응답할 데이터 (비밀번호 제외)
class UserResponse(BaseModel):
    """
    사용자 정보 응답 스키마

    login_id: 사용자 ID
    user_real_name: 실명 (옵션)
    email: 이메일 (옵션)
    age_range: 연령대
    gender: 성별
    subscribed_categories: 구독한 카테고리 이름 목록
    subscribed_keywords: 구독한 키워드 텍스트 목록
    marketing_agree: 마케팅 동의
    user_status: 상태
    """

    id: int
    login_id: str
    user_real_name: Optional[str] = None
    email: Optional[str] = None
    age_range: Optional[str] = None
    gender: Optional[str] = None

    # ORM 관계에서 이름만 추출해서 리스트로 줄 예정
    subscribed_categories: List[str] = []
    subscribed_keywords: List[str] = []

    marketing_agree: bool = False
    created_at: Optional[datetime] = None
    user_status: int = 1

    class Config:
        from_attributes = True


class LogViewRequest(BaseModel):
    """
    사용자가 읽은 키워드나 카테고리 업데이트 요청 스키마

    login_id: 사용자 ID
    category: 읽은 카테고리 이름
    keywords: 읽은 키워드 텍스트 목록 (옵션)
    """

    login_id: str
    category: Optional[str] = None
    keywords: Optional[List[str]] = None


# 사용자 정보 수정
class UserUpdate(BaseModel):
    """
    사용자 정보 수정 요청 스키마.
    """

    user_real_name: Optional[str] = None
    password: Optional[str] = None  # 변경 시
    email: Optional[str] = None
    age_range: Optional[str] = None
    gender: Optional[str] = None
    subscribed_categories: Optional[List[str]] = None
    subscribed_keywords: Optional[List[str]] = None
    fcm_token: Optional[str] = None
    marketing_agree: Optional[bool] = None
    user_status: Optional[int] = None


class UserLoginRequest(BaseModel):
    """
    로그인 요청 스키마
    """

    login_id: str
    password: str


# --- 추가된 스키마 ---
class ArticleResponse(BaseModel):
    """
    뉴스 기사 응답 스키마 (ArticleResponse)

    id: 기사 ID
    title: 기사 제목
    contents: 기사 내용 (옵션)
    img_urls: 기사 내 사진 URL 목록 (옵션)
    url: 기사 URL
    company_name: 언론사명 (Company 테이블의 name)
    created_at: 기사 발행 시각
    region: 'domestic' | 'global'
    """

    id: int
    title: Optional[str] = None
    contents: Optional[str] = None
    img_urls: Optional[List[str]] = None
    url: str
    company_name: str
    created_at: datetime
    region: str

    class Config:
        from_attributes = True


class IssueResponse(BaseModel):
    """
    AI 생성 기사 응답 스키마 (IssueResponse)

    id: 기사 ID
    title: 기사 제목
    contents: 기사 내용
    created_at: 기사 생성 시각
    analysis_result: AI 비교분석 (JSON)
    keywords: 키워드 (JSON)
    """

    id: int
    cluster_id: int
    title: Optional[str] = None
    contents: Optional[str] = None
    created_at: datetime
    analysis_result: Optional[Any]
    keywords: Optional[List[str]] = None

    # 반응/조회수 (옵션)
    like_count: int = 0
    dislike_count: int = 0

    class Config:
        from_attributes = True
