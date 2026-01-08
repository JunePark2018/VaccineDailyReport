from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr
from datetime import datetime

# --- [Pydantic 모델] 프론트엔드에 보낼 데이터 형태 정의 ---
class ArticleResponse(BaseModel):
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
    id: int
    title: str
    content: str
    created_at: datetime
    # 통째로 구조화된 JSON 데이터를 보냅니다. (프론트엔드가 받아서 알아서 뿌림)
    analysis_result: Optional[Any] 

    class Config:
        from_attributes = True

# 회원가입 요청 시 받을 데이터
class UserCreateRequest(BaseModel):
    login_id: str
    password_hash: str  # 실제로는 비밀번호 원문을 받아 내부에서 해싱하는 것이 좋지만, 현재 구조에 맞췄습니다.
    user_real_name: Optional[str] = None
    email: Optional[str] = None
    subscribed_categories: Optional[List[str]] = []
    subscribed_keywords: Optional[List[str]] = []
    marketing_agree: bool = False

# 클라이언트에게 응답할 데이터 (비밀번호 제외)
class UserResponse(BaseModel):
    login_id: str
    user_real_name: Optional[str] = None
    email: Optional[str] = None
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

# 누가, 어떤 카테고리, 어떤 키워드의 글을 봤는지 데이터를 보낼 때 사용할 포멧
class LogViewRequest(BaseModel):
    login_id: str
    category: str
    keywords: Optional[List[str]] = None

# 사용자 정보 수정
class UserUpdate(BaseModel):
    user_real_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    subscribed_categories: Optional[List[str]] = None
    subscribed_keywords: Optional[List[str]] = None
    fcm_token: Optional[str] = None
    marketing_agree: Optional[bool] = None
    user_status: Optional[int] = None

class UserLoginRequest(BaseModel):
    login_id: str
    password: str