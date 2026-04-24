from datetime import datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import WorkerCode
from app.schemas import WorkerCodeCreate, WorkerCodeRead, WorkerCodeUpdate

router = APIRouter(prefix="/worker-codes", tags=["Worker Codes"])


@router.get("/", response_model=list[WorkerCodeRead])
def list_worker_codes(db: Session = Depends(get_db)):
    """Return all worker codes, newest first."""
    return db.query(WorkerCode).order_by(WorkerCode.start_date.desc()).all()


@router.get("/active", response_model=list[WorkerCodeRead])
def list_active_worker_codes(db: Session = Depends(get_db)):
    """Return only worker codes that have no end date (still active).
    Used to populate the Workers tab FK dropdown."""
    return (
        db.query(WorkerCode)
        .filter(WorkerCode.end_date == None)
        .order_by(WorkerCode.code_name)
        .all()
    )


@router.get("/{code_id}", response_model=WorkerCodeRead)
def get_worker_code(code_id: UUID, db: Session = Depends(get_db)):
    wc = db.query(WorkerCode).filter_by(code_id=code_id).first()
    if not wc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker code not found.")
    return wc


@router.post("/", response_model=WorkerCodeRead, status_code=status.HTTP_201_CREATED)
def create_worker_code(payload: WorkerCodeCreate, db: Session = Depends(get_db)):
    """Create a new worker code. start_date is set automatically."""
    import uuid6
    wc = WorkerCode(
        code_id=uuid6.uuid7(),
        code_name=payload.code_name,
        code_description=payload.code_description,
        pay_rate=payload.pay_rate,
        start_date=datetime.now(),
        end_date=None,
    )
    db.add(wc)
    db.commit()
    db.refresh(wc)
    return wc


@router.patch("/{code_id}", response_model=WorkerCodeRead)
def update_worker_code(code_id: UUID, payload: WorkerCodeUpdate,
                       db: Session = Depends(get_db)):
    """Partially update editable fields on a worker code."""
    wc = db.query(WorkerCode).filter_by(code_id=code_id).first()
    if not wc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker code not found.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(wc, field, value)
    db.commit()
    db.refresh(wc)
    return wc


@router.post("/{code_id}/end", response_model=WorkerCodeRead)
def end_worker_code(code_id: UUID, db: Session = Depends(get_db)):
    """Set end_date to now, marking this worker code as inactive."""
    wc = db.query(WorkerCode).filter_by(code_id=code_id).first()
    if not wc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker code not found.")
    if wc.end_date is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Worker code is already ended.")
    wc.end_date = datetime.now()
    db.commit()
    db.refresh(wc)
    return wc

