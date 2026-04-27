from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class Settings(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    int_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    str_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bool_value: Mapped[bool | None] = mapped_column(Boolean, nullable=True)