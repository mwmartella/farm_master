from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Uuid, Numeric, DateTime, ForeignKey, Time
from app.db import Base
from datetime import date, datetime, time
from decimal import Decimal
import uuid6


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[uuid6.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid6.uuid7
    )

    worker_code: Mapped[uuid6.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("worker_codes.code_id"), nullable=False
    )
    # our farm's code for the worker type, ie. C2
    # this will be FKed to the worker code table when its built.

    first_name: Mapped[str] = mapped_column(String(100))

    last_name: Mapped[str] = mapped_column(String(100))

    start_date: Mapped[date] = mapped_column(Date, nullable=False)

    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # When end_date is NULL the worker is active.
    # When end_date is set the worker is no longer active.


class WorkerCode(Base):
    __tablename__ = "worker_codes"

    code_id: Mapped[uuid6.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid6.uuid7
    )

    code_name: Mapped[str] = mapped_column(String(100))

    code_description: Mapped[str] = mapped_column(String(255))

    pay_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class WorkerTime(Base):
    __tablename__ = "worker_times"

    time_id: Mapped[uuid6.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid6.uuid7
    )

    time_name: Mapped[str] = mapped_column(String(100))

    start_time: Mapped[time] = mapped_column(Time(timezone=True), nullable=False)

    end_time: Mapped[time | None] = mapped_column(Time(timezone=True), nullable=True)

    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
