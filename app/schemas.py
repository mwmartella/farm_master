from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ─────────────────────────────────────────────
# WorkerCode Schemas
# ─────────────────────────────────────────────

class WorkerCodeCreate(BaseModel):
    """Fields required to create a new WorkerCode.
    start_date is set automatically on the server side."""
    code_name: str
    code_description: str
    pay_rate: Decimal


class WorkerCodeUpdate(BaseModel):
    """All fields are optional — only provided fields will be updated.
    Timestamps and IDs are never updatable."""
    code_name: str | None = None
    code_description: str | None = None
    pay_rate: Decimal | None = None


class WorkerCodeRead(BaseModel):
    """Full representation returned from the database."""
    model_config = ConfigDict(from_attributes=True)

    code_id: UUID
    code_name: str
    code_description: str
    pay_rate: Decimal
    start_date: datetime
    end_date: datetime | None


# ─────────────────────────────────────────────
# Worker Schemas
# ─────────────────────────────────────────────

class WorkerCreate(BaseModel):
    """Fields required to create a new Worker.
    start_date is set automatically on the server side."""
    worker_code: UUID  # FK to WorkerCode.code_id
    first_name: str
    last_name: str


class WorkerUpdate(BaseModel):
    """Only the hand-typed fields are editable.
    Worker code FK and timestamps are never updatable."""
    first_name: str | None = None
    last_name: str | None = None


class WorkerRead(BaseModel):
    """Full representation returned from the database."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    worker_code: UUID
    first_name: str
    last_name: str
    start_date: date
    end_date: date | None


# ─────────────────────────────────────────────
# WorkerTime Schemas
# ─────────────────────────────────────────────

class WorkerTimeCreate(BaseModel):
    """Fields required to create a new WorkerTime.
    start_date is set automatically on the server side."""
    time_name: str
    start_time: time
    end_time: time | None = None


class WorkerTimeUpdate(BaseModel):
    """Only the hand-typed fields are editable.
    Timestamps are never updatable."""
    time_name: str | None = None
    start_time: time | None = None
    end_time: time | None = None


class WorkerTimeRead(BaseModel):
    """Full representation returned from the database."""
    model_config = ConfigDict(from_attributes=True)

    time_id: UUID
    time_name: str
    start_time: time
    end_time: time | None
    start_date: datetime
    end_date: datetime | None

