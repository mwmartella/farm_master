from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import FruitType, Rootstock
from app.schemas import RootstockCreate, RootstockRead, RootstockUpdate

router = APIRouter(prefix="/rootstocks", tags=["Rootstocks"])


@router.get("/", response_model=list[RootstockRead])
def list_rootstocks(db: Session = Depends(get_db)):
    return db.query(Rootstock).order_by(Rootstock.name).all()


@router.get("/{rootstock_id}", response_model=RootstockRead)
def get_rootstock(rootstock_id: UUID, db: Session = Depends(get_db)):
    rs = db.query(Rootstock).filter_by(id=rootstock_id).first()
    if not rs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rootstock not found.")
    return rs


@router.post("/", response_model=RootstockRead, status_code=status.HTTP_201_CREATED)
def create_rootstock(payload: RootstockCreate, db: Session = Depends(get_db)):
    ft = db.query(FruitType).filter_by(id=payload.fruit_type_id).first()
    if not ft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fruit type not found.")
    existing = db.query(Rootstock).filter_by(name=payload.name, fruit_type_id=payload.fruit_type_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Rootstock '{payload.name}' already exists for this fruit type.")
    rs = Rootstock(
        name=payload.name,
        fruit_type_id=payload.fruit_type_id,
        vigour_class=payload.vigour_class,
        notes=payload.notes,
    )
    db.add(rs)
    db.commit()
    db.refresh(rs)
    return rs


@router.patch("/{rootstock_id}", response_model=RootstockRead)
def update_rootstock(rootstock_id: UUID, payload: RootstockUpdate, db: Session = Depends(get_db)):
    rs = db.query(Rootstock).filter_by(id=rootstock_id).first()
    if not rs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rootstock not found.")

    updates = payload.model_dump(exclude_none=True)

    if "name" in updates and updates["name"] != rs.name:
        existing = db.query(Rootstock).filter_by(
            name=updates["name"], fruit_type_id=rs.fruit_type_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Rootstock '{updates['name']}' already exists for this fruit type.")

    for key, value in updates.items():
        setattr(rs, key, value)

    db.commit()
    db.refresh(rs)
    return rs


@router.delete("/{rootstock_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rootstock(rootstock_id: UUID, db: Session = Depends(get_db)):
    rs = db.query(Rootstock).filter_by(id=rootstock_id).first()
    if not rs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rootstock not found.")
    db.delete(rs)
    db.commit()

