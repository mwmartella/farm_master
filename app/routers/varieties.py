from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import FruitType, Variety
from app.schemas import VarietyCreate, VarietyRead, VarietyUpdate

router = APIRouter(prefix="/varieties", tags=["Varieties"])


@router.get("/", response_model=list[VarietyRead])
def list_varieties(db: Session = Depends(get_db)):
    return db.query(Variety).order_by(Variety.name).all()


@router.get("/{variety_id}", response_model=VarietyRead)
def get_variety(variety_id: UUID, db: Session = Depends(get_db)):
    v = db.query(Variety).filter_by(id=variety_id).first()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Variety not found.")
    return v


@router.post("/", response_model=VarietyRead, status_code=status.HTTP_201_CREATED)
def create_variety(payload: VarietyCreate, db: Session = Depends(get_db)):
    # Validate FK
    ft = db.query(FruitType).filter_by(id=payload.fruit_type_id).first()
    if not ft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Fruit type not found.")
    # Check unique(name, fruit_type_id)
    existing = db.query(Variety).filter_by(
        name=payload.name, fruit_type_id=payload.fruit_type_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Variety '{payload.name}' already exists for this fruit type.")
    v = Variety(name=payload.name, fruit_type_id=payload.fruit_type_id)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


@router.patch("/{variety_id}", response_model=VarietyRead)
def update_variety(variety_id: UUID, payload: VarietyUpdate,
                   db: Session = Depends(get_db)):
    v = db.query(Variety).filter_by(id=variety_id).first()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Variety not found.")

    updates = payload.model_dump(exclude_none=True)

    if "name" in updates and updates["name"] != v.name:
        existing = db.query(Variety).filter_by(
            name=updates["name"], fruit_type_id=v.fruit_type_id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Variety '{updates['name']}' already exists for this fruit type.")

    for key, value in updates.items():
        setattr(v, key, value)

    db.commit()
    db.refresh(v)
    return v


@router.delete("/{variety_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variety(variety_id: UUID, db: Session = Depends(get_db)):
    v = db.query(Variety).filter_by(id=variety_id).first()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Variety not found.")
    db.delete(v)
    db.commit()

