from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import WorkerTime
from app.schemas import WorkerTimeCreate, WorkerTimeRead, WorkerTimeUpdate

router = APIRouter(prefix="/worker-times", tags=["Worker Times"])


@router.get("/", response_model=list[WorkerTimeRead])
def list_worker_times(db: Session = Depends(get_db)):
    """Return all worker times, newest first."""
    return db.query(WorkerTime).order_by(WorkerTime.start_date.desc()).all()


@router.get("/active", response_model=list[WorkerTimeRead])
def list_active_worker_times(db: Session = Depends(get_db)):
    """Return only worker times with no end date (still active)."""
    return (
        db.query(WorkerTime)
        .filter(WorkerTime.end_date == None)
        .order_by(WorkerTime.time_name)
        .all()
    )


@router.get("/{time_id}", response_model=WorkerTimeRead)
def get_worker_time(time_id: UUID, db: Session = Depends(get_db)):
    wt = db.query(WorkerTime).filter_by(time_id=time_id).first()
    if not wt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker time not found.")
    return wt


@router.post("/", response_model=WorkerTimeRead, status_code=status.HTTP_201_CREATED)
def create_worker_time(payload: WorkerTimeCreate, db: Session = Depends(get_db)):
    """Create a new worker time. start_date is set automatically."""
    import uuid6
    wt = WorkerTime(
        time_id=uuid6.uuid7(),
        time_name=payload.time_name,
        start_time=payload.start_time,
        end_time=payload.end_time,
        start_date=datetime.now(),
        end_date=None,
    )
    db.add(wt)
    db.commit()
    db.refresh(wt)
    return wt


@router.patch("/{time_id}", response_model=WorkerTimeRead)
def update_worker_time(time_id: UUID, payload: WorkerTimeUpdate,
                       db: Session = Depends(get_db)):
    """Partially update editable fields on a worker time."""
    wt = db.query(WorkerTime).filter_by(time_id=time_id).first()
    if not wt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker time not found.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(wt, field, value)
    db.commit()
    db.refresh(wt)
    return wt


@router.post("/{time_id}/end", response_model=WorkerTimeRead)
def end_worker_time(time_id: UUID, db: Session = Depends(get_db)):
    """Set end_date to now, marking this worker time as inactive."""
    wt = db.query(WorkerTime).filter_by(time_id=time_id).first()
    if not wt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker time not found.")
    if wt.end_date is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Worker time is already ended.")
    wt.end_date = datetime.now()
    db.commit()
    db.refresh(wt)
    return wt

