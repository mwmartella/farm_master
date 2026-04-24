from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Worker, WorkerCode
from app.schemas import WorkerCreate, WorkerRead, WorkerUpdate

router = APIRouter(prefix="/workers", tags=["Workers"])


@router.get("/", response_model=list[WorkerRead])
def list_workers(db: Session = Depends(get_db)):
    """Return all workers, newest first."""
    return db.query(Worker).order_by(Worker.start_date.desc()).all()


@router.get("/active", response_model=list[WorkerRead])
def list_active_workers(db: Session = Depends(get_db)):
    """Return only workers with no end date (still active)."""
    return (
        db.query(Worker)
        .filter(Worker.end_date == None)
        .order_by(Worker.last_name, Worker.first_name)
        .all()
    )


@router.get("/{worker_id}", response_model=WorkerRead)
def get_worker(worker_id: UUID, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter_by(id=worker_id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker not found.")
    return worker


@router.post("/", response_model=WorkerRead, status_code=status.HTTP_201_CREATED)
def create_worker(payload: WorkerCreate, db: Session = Depends(get_db)):
    """Create a new worker. start_date is set automatically to today."""
    import uuid6

    # Validate FK exists and is active
    wc = db.query(WorkerCode).filter_by(code_id=payload.worker_code).first()
    if not wc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker code not found.")
    if wc.end_date is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Cannot assign an inactive worker code.")

    worker = Worker(
        id=uuid6.uuid7(),
        worker_code=payload.worker_code,
        first_name=payload.first_name,
        last_name=payload.last_name,
        start_date=date.today(),
        end_date=None,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.patch("/{worker_id}", response_model=WorkerRead)
def update_worker(worker_id: UUID, payload: WorkerUpdate,
                  db: Session = Depends(get_db)):
    """Partially update editable fields (first_name, last_name) on a worker."""
    worker = db.query(Worker).filter_by(id=worker_id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker not found.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(worker, field, value)
    db.commit()
    db.refresh(worker)
    return worker


@router.post("/{worker_id}/end", response_model=WorkerRead)
def end_worker(worker_id: UUID, db: Session = Depends(get_db)):
    """Set end_date to today, marking this worker as inactive."""
    worker = db.query(Worker).filter_by(id=worker_id).first()
    if not worker:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Worker not found.")
    if worker.end_date is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Worker is already ended.")
    worker.end_date = date.today()
    db.commit()
    db.refresh(worker)
    return worker

