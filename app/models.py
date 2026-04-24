from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Uuid
from app.db import Base
import uuid6


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[uuid6.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid6.uuid7
    )

    worker_code: Mapped[str] = mapped_column(String(50))
    # our farm's code for the worker type, ie. C2
    # this will be FKed to the worker code table when its built.

    first_name: Mapped[str] = mapped_column(String(100))

    last_name: Mapped[str] = mapped_column(String(100))

    start_date: Mapped[Date] = mapped_column(Date, nullable=False)

    end_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    # When end_date is NULL the worker is active.
    # When end_date is set the worker is no longer active.
