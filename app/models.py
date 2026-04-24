from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean
from app.db import Base


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(primary_key=True)

    worker_code: Mapped[str] = mapped_column(String(50), unique=True)

    first_name: Mapped[str] = mapped_column(String(100))

    last_name: Mapped[str] = mapped_column(String(100))

    active: Mapped[bool] = mapped_column(Boolean, default=True)