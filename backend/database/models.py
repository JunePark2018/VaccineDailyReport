from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey,
    DateTime,
    JSON,
    Enum,
    Table,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

Base = declarative_base()

# -------------------------
# Cluster <-> News (M:N)
# -------------------------
cluster_news_link = Table(
    "cluster_news_link",
    Base.metadata,
    Column("cluster_id", ForeignKey("clusters.id", ondelete="CASCADE"), primary_key=True),
    Column("news_id", ForeignKey("news.id", ondelete="CASCADE"), primary_key=True),
)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    # DB에서 표준으로 쓰는 이름(중복 방지용)
    name = Column(String(100), unique=True, nullable=False, index=True)

    # UI에 보여줄 이름이 따로 필요하면(선택)
    display_name = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    aliases = relationship("CompanyAlias", back_populates="company", lazy="selectin", cascade="all, delete-orphan")
    news = relationship("News", back_populates="company", lazy="selectin")


class CompanyAlias(Base):
    __tablename__ = "company_aliases"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    alias = Column(String(100), unique=True, nullable=False, index=True)

    company = relationship("Company", back_populates="aliases")


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    news = relationship(
        "News",
        secondary=cluster_news_link,
        back_populates="clusters",
        lazy="selectin",
    )

    ai_generated_news = relationship(
        "AiGeneratedNews",
        back_populates="cluster",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    contents = Column(Text, nullable=True)

    url = Column(String, unique=True, nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True)
    company = relationship("Company", back_populates="news")

    img_urls = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    region = Column(Enum("domestic", "global", name="news_region"), nullable=False, index=True)

    clusters = relationship(
        "Cluster",
        secondary=cluster_news_link,
        back_populates="news",
        lazy="selectin",
    )

    @hybrid_property
    def company_name(self):
        return self.company.name if self.company else None


class AiGeneratedNews(Base):
    __tablename__ = "ai_generated_news"

    id = Column(Integer, primary_key=True, index=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String, nullable=True)
    contents = Column(Text, nullable=True)

    keywords = Column(JSON, nullable=True)
    analysis_result = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # 캐시 컬럼(선택)
    like_count = Column(Integer, default=0, nullable=False)
    dislike_count = Column(Integer, default=0, nullable=False)

    cluster = relationship("Cluster", back_populates="ai_generated_news")

    reactions = relationship("NewsReaction", back_populates="news", cascade="all, delete-orphan")
    views = relationship("NewsView", back_populates="news", cascade="all, delete-orphan")


# -------------------------
# User
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login_id = Column(String(50), unique=True, nullable=False, index=True)

    user_real_name = Column(String(50), nullable=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)

    age_range = Column(String(30), nullable=True)
    gender = Column(String(30), nullable=True)

    fcm_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    marketing_agree = Column(Boolean, default=False, nullable=False)
    user_status = Column(Integer, default=1, nullable=False)

    reactions = relationship("NewsReaction", back_populates="user", cascade="all, delete-orphan")
    views = relationship("NewsView", back_populates="user", cascade="all, delete-orphan")
    searches = relationship("SearchLog", back_populates="user", cascade="all, delete-orphan")

    keyword_stats = relationship(
        "UserKeywordReadStat",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    category_stats = relationship(
        "UserCategoryReadStat",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    subscribed_categories = relationship(
        "Category", secondary="user_category_subscriptions", back_populates="subscribers"
    )
    keyword_subscriptions = relationship(
        "UserKeywordSubscription",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class UserKeywordSubscription(Base):
    __tablename__ = "user_keyword_subscriptions"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    keyword = Column(String(200), primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="keyword_subscriptions")


# -------------------------
# Like/Dislike (AiGeneratedNews만)
# -------------------------
class NewsReaction(Base):
    __tablename__ = "news_reactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    news_id = Column(Integer, ForeignKey("ai_generated_news.id", ondelete="CASCADE"), nullable=False, index=True)

    value = Column(Integer, nullable=False)  # 1=like, -1=dislike
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="reactions")
    news = relationship("AiGeneratedNews", back_populates="reactions")

    __table_args__ = (
        UniqueConstraint("user_id", "news_id", name="uq_user_news_reaction"),
        CheckConstraint("value in (1, -1)", name="ck_reaction_value"),
    )


# -------------------------
# View History (AiGeneratedNews id 기반)
# -------------------------
class NewsView(Base):
    __tablename__ = "news_views"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    news_id = Column(Integer, ForeignKey("ai_generated_news.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("user_id", "news_id", name="uq_user_news_view"),)

    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="views")
    news = relationship("AiGeneratedNews", back_populates="views")


# -------------------------
# Search History
# -------------------------
class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    query = Column(String(255), nullable=False)
    searched_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="searches")


# -------------------------
# Category / Keyword + Subscriptions
# -------------------------
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False, index=True)

    subscribers = relationship("User", secondary="user_category_subscriptions", back_populates="subscribed_categories")


user_category_subscriptions = Table(
    "user_category_subscriptions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


# -------------------------
# Read stats
# -------------------------
class UserCategoryReadStat(Base):
    __tablename__ = "user_category_read_stats"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)

    read_count = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="category_stats")


class UserKeywordReadStat(Base):
    __tablename__ = "user_keyword_read_stats"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    keyword = Column(String(200), primary_key=True)
    count = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="keyword_stats")
