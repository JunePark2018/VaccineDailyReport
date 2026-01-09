from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- [Pydantic 모델] 프론트엔드에 보낼 데이터 형태 정의 ---
class ArticleResponse(BaseModel):
    """
    뉴스 기사 응답 스키마<br/><br/>
    
    id: 기사 ID<br/>
    title: 기사 제목<br/>
    contents: 기사 내용 (옵션)<br/>
    category: 카테고리<br/>
    url: 기사 URL<br/>
    company_name: 언론사명<br/>
    img_urls: 기사 내 사진 URL 목록 (옵션)<br/>
    time: 기사 발행 시각 (옵션)<br/>
    author: 기자 이름<br/>
    """
    id: int
    title: str
    contents: Optional[str] = None          # 본문
    category: str
    url: str
    company_name: str
    img_urls: Optional[List[str]] = None
    time: Optional[datetime]
    author: str

    class Config:
        from_attributes = True

class IssueResponse(BaseModel):
    """
    AI 생성 기사 응답 스키마<br/><br/>
    
    id: 기사 ID<br/>
    title: 기사 제목<br/>
    content: 기사 내용<br/>
    created_at: 기사 생성 시각
    analysis_result: AI 비교분석 (옵션)
    """
    id: int
    title: str
    contents: str
    created_at: datetime
    # 통째로 구조화된 JSON 데이터를 보냅니다. (프론트엔드가 받아서 알아서 뿌림)
    analysis_result: Optional[Any] 

    class Config:
        from_attributes = True

# 회원가입 요청 시 받을 데이터
class UserCreateRequest(BaseModel):
    """
    회원가입 요청 시 받을 스키마<br/><br/>
    
    login_id: 사용자 ID<br/>
    password_hash: 비밀번호 해시<br/>
    user_real_name: 실명 (옵션)<br/>
    email: 이메일 (옵션)
    age_range: 연령대
    gender: 성별
    subscribed_categories: 구독한 카테고리 목록 (옵션)
    subscribed_keywords: 구독한 키워드 목록 (옵션)
    marketing_agree: 마케팅 동의
    """
    login_id: str
    password_hash: str  # 실제로는 비밀번호 원문을 받아 내부에서 해싱하는 것이 좋지만, 현재 구조에 맞췄습니다.
    user_real_name: Optional[str] = None
    email: Optional[str] = None
    age_range: str
    gender: str
    subscribed_categories: Optional[List[str]] = []
    subscribed_keywords: Optional[List[str]] = []
    marketing_agree: bool = False

# 클라이언트에게 응답할 데이터 (비밀번호 제외)
class UserResponse(BaseModel):
    """
    사용자 정보 응답 스키마<br/><br/>
    
    login_id: 사용자 ID<br/>
    user_real_name: 실명 (옵션)<br/>
    email: 이메일 (옵션)
    age_range: 연령대
    gender: 성별
    subscribed_categories: 구독한 카테고리 목록 (옵션)
    subscribed_keywords: 구독한 키워드 목록 (옵션)
    read_categories: 읽은 카테고리 및 읽은 횟수 딕셔너리: {"세계": 27, "IT/과학": 38} (옵션)
    read_keywords: 읽은 키워드 및 읽은 횟수 딕셔너리: {"삼성전자": 86, "우크라이나": 47} (옵션)
    marketing_agree: 마케팅 동의
    """
    login_id: str
    user_real_name: Optional[str] = None
    email: Optional[str] = None
    age_range: str
    gender: str
    subscribed_categories: Optional[List[str]] = []
    subscribed_keywords: Optional[List[str]] = []
    read_categories: Optional[Dict[str, int]] = {}
    read_keywords: Optional[Dict[str, int]] = {}
    marketing_agree: bool = False
    
    # 시스템이 생성하는 정보 (가입일, 상태 등)
    created_at: Optional[datetime] = None 
    user_status: int = 1 

    class Config:
        from_attributes = True

class LogViewRequest(BaseModel):
    """
    사용자가 읽은 키워드나 카테고리 업데이트 요청 스키마<br/><br/>
    
    login_id: 사용자 ID<br/>
    category: 읽은 카테고리
    keywords: 읽은 키워드 목록 (옵션)
    """
    login_id: str
    category: str
    keywords: Optional[List[str]] = None

# 사용자 정보 수정
class UserUpdate(BaseModel):
    """
    사용자 정보 수정 요청 스키마. (모든 파라미터가 옵션이므로, 수정할 사항만 넣으면 됩니다.)<br/><br/>
    
    user_real_name: 실명 (옵션)<br/>
    password: 비밀번호 해시 (옵션)<br/>
    email: 이메일 (옵션)
    age_range: 연령대
    gender: 성별
    subscribed_categories: 구독한 카테고리 목록 (옵션)
    subscribed_keywords: 구독한 키워드 목록 (옵션)
    fcm_token: FCM 토큰 (옵션)
    marketing_agree: 마케팅 동의 (옵션)
    user_status: 휴면 여부 (옵션)
    """
    
    user_real_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    age_range: str
    gender: str
    subscribed_categories: Optional[List[str]] = None
    subscribed_keywords: Optional[List[str]] = None
    fcm_token: Optional[str] = None
    marketing_agree: Optional[bool] = None
    user_status: Optional[int] = None

class UserLoginRequest(BaseModel):
    """
    로그인 요청 스키마
    
    login_id: 사용자 ID
    password: 사용자 비밀번호
    """
    login_id: str
    password: str