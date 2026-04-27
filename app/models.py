from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Date, Uuid, Numeric, DateTime, ForeignKey, Time, func, text, UniqueConstraint, Integer
from app.db import Base
from datetime import date, datetime, time
from decimal import Decimal
import uuid6
import uuid


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


class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    code: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class FruitType(Base):
    __tablename__ = "fruit_types"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Variety(Base):
    __tablename__ = "varieties"
    __table_args__ = (UniqueConstraint("name", "fruit_type_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    fruit_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("fruit_types.id"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Block(Base):
    __tablename__ = "blocks"
    __table_args__ = (UniqueConstraint("field_id", "name"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    field_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("fields.id"), nullable=False
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    code: Mapped[str | None] = mapped_column(String, nullable=True)

    block_type: Mapped[str | None] = mapped_column(String, nullable=True)

    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class BlockRow(Base):
    __tablename__ = "block_rows"
    __table_args__ = (UniqueConstraint("block_id", "row_number", "side"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    block_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("blocks.id"), nullable=False
    )

    row_number: Mapped[int] = mapped_column(Integer, nullable=False)

    side: Mapped[str | None] = mapped_column(String(1), nullable=True)

    variety_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("varieties.id"), nullable=False
    )

    clone_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("variety_clones.id"), nullable=True
    )

    rootstock_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("rootstocks.id"), nullable=True
    )

    planting_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    row_width_m: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)

    tree_spacing_m: Mapped[Decimal | None] = mapped_column(Numeric(6, 2), nullable=True)

    tree_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    row_length_m: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)

    area_m2: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Rootstock(Base):
    __tablename__ = "rootstocks"
    __table_args__ = (UniqueConstraint("name", "fruit_type_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    fruit_type_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("fruit_types.id"), nullable=False
    )

    vigour_class: Mapped[str | None] = mapped_column(String, nullable=True)

    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class VarietyClone(Base):
    __tablename__ = "variety_clones"
    __table_args__ = (UniqueConstraint("name", "variety_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    variety_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("varieties.id"), nullable=False
    )

    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Field(Base):
    __tablename__ = "fields"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    code: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    site_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("sites.id"), nullable=True
    )

    gross_area_ha: Mapped[Decimal | None] = mapped_column(Numeric(8, 3), nullable=True)

    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name: Mapped[str] = mapped_column(String, nullable=False)

    code: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    business_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("businesses.id"), nullable=True
    )

    type: Mapped[str] = mapped_column(String, nullable=False)

    address: Mapped[str] = mapped_column(String, nullable=False)

    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


