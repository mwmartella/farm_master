from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import BlockRow, RowPortion, Variety, VarietyClone, Rootstock
from app.schemas import RowPortionCreate, RowPortionRead, RowPortionUpdate

router = APIRouter(prefix="/row-portions", tags=["Row Portions"])


@router.get("/", response_model=list[RowPortionRead])
def list_row_portions(row_id: UUID | None = None, db: Session = Depends(get_db)):
    q = db.query(RowPortion)
    if row_id:
        q = q.filter_by(row_id=row_id)
    return q.order_by(RowPortion.row_id, RowPortion.sequence_no).all()


@router.get("/{portion_id}", response_model=RowPortionRead)
def get_row_portion(portion_id: UUID, db: Session = Depends(get_db)):
    p = db.query(RowPortion).filter_by(id=portion_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Row portion not found.")
    return p


@router.post("/", response_model=RowPortionRead, status_code=status.HTTP_201_CREATED)
def create_row_portion(payload: RowPortionCreate, db: Session = Depends(get_db)):
    if not db.query(BlockRow).filter_by(id=payload.row_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block row not found.")
    if not db.query(Variety).filter_by(id=payload.variety_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variety not found.")
    if payload.clone_id and not db.query(VarietyClone).filter_by(id=payload.clone_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variety clone not found.")
    if payload.rootstock_id and not db.query(Rootstock).filter_by(id=payload.rootstock_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rootstock not found.")

    p = RowPortion(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.patch("/{portion_id}", response_model=RowPortionRead)
def update_row_portion(portion_id: UUID, payload: RowPortionUpdate, db: Session = Depends(get_db)):
    p = db.query(RowPortion).filter_by(id=portion_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Row portion not found.")

    updates = payload.model_dump(exclude_none=True)

    if "variety_id" in updates and not db.query(Variety).filter_by(id=updates["variety_id"]).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variety not found.")
    if "clone_id" in updates and updates["clone_id"] and not db.query(VarietyClone).filter_by(id=updates["clone_id"]).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variety clone not found.")
    if "rootstock_id" in updates and updates["rootstock_id"] and not db.query(Rootstock).filter_by(id=updates["rootstock_id"]).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rootstock not found.")

    for key, value in updates.items():
        setattr(p, key, value)

    db.commit()
    db.refresh(p)
    return p


@router.delete("/{portion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_row_portion(portion_id: UUID, db: Session = Depends(get_db)):
    p = db.query(RowPortion).filter_by(id=portion_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Row portion not found.")
    db.delete(p)
    db.commit()

