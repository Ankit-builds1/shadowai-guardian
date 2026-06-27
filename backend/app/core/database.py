from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PromptScan(Base):
    __tablename__ = "prompt_scans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    original_text: Mapped[str] = mapped_column(Text)
    safe_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(40), default="prompt")
    category: Mapped[str] = mapped_column(String(120))
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(40), index=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    injection_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    ml_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    entities: Mapped[list["DetectedEntity"]] = relationship(back_populates="scan", cascade="all, delete-orphan")


class DetectedEntity(Base):
    __tablename__ = "detected_entities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("prompt_scans.id"))
    entity_type: Mapped[str] = mapped_column(String(80))
    redacted_value: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(String(40))
    confidence: Mapped[float] = mapped_column(Float)
    start_index: Mapped[int] = mapped_column(Integer)
    end_index: Mapped[int] = mapped_column(Integer)
    scan: Mapped[PromptScan] = relationship(back_populates="entities")


class DocumentScan(Base):
    __tablename__ = "document_scans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(40))
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(40))
    entity_count: Mapped[int] = mapped_column(Integer)
    injection_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RepoScan(Base):
    __tablename__ = "repo_scans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    repo_name: Mapped[str] = mapped_column(String(255))
    repo_url: Mapped[str] = mapped_column(Text)
    files_scanned: Mapped[int] = mapped_column(Integer)
    secrets_found: Mapped[int] = mapped_column(Integer)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    findings: Mapped[list["RepoFileFinding"]] = relationship(back_populates="repo_scan", cascade="all, delete-orphan")


class RepoFileFinding(Base):
    __tablename__ = "repo_file_findings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    repo_scan_id: Mapped[int] = mapped_column(ForeignKey("repo_scans.id"))
    file_path: Mapped[str] = mapped_column(Text)
    entity_type: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(40))
    line_number: Mapped[int] = mapped_column(Integer)
    redacted_value: Mapped[str] = mapped_column(Text)
    repo_scan: Mapped[RepoScan] = relationship(back_populates="findings")


class ToolRiskScore(Base):
    __tablename__ = "tool_risk_scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    domain: Mapped[str] = mapped_column(String(255), index=True)
    tool_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_known_tool: Mapped[bool] = mapped_column(Boolean)
    is_https: Mapped[bool] = mapped_column(Boolean)
    user_trust_status: Mapped[str] = mapped_column(String(80))
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PrivacyScore(Base):
    __tablename__ = "privacy_scores"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    month: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    total_scans: Mapped[int] = mapped_column(Integer)
    critical_count: Mapped[int] = mapped_column(Integer)
    high_count: Mapped[int] = mapped_column(Integer)
    medium_count: Mapped[int] = mapped_column(Integer)
    low_count: Mapped[int] = mapped_column(Integer)
    safe_count: Mapped[int] = mapped_column(Integer)
    privacy_score: Mapped[int] = mapped_column(Integer)
    grade: Mapped[str] = mapped_column(String(8))
    improvement_percent: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
