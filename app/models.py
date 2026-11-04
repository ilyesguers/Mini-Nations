from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Index, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GameRound(Base):
    __tablename__ = "game_rounds"
    __table_args__ = (Index("ix_game_rounds_game_recorded_at", "game", "recorded_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    game: Mapped[str] = mapped_column(String(24), nullable=False)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    multiplier: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source: Mapped[str] = mapped_column(String(24), default="manual", nullable=False)
    details: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
