from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models import Block, BlockRow
from app.schemas import BlockRowCreate, BlockRowRead, BlockRowUpdate

VALID_SIDES = {"N", "S", "E", "W"}

router = APIRouter(prefix="/block-rows", tags=["Block Rows"])


@router.get("/", response_model=list[BlockRowRead])
def list_block_rows(block_id: UUID | None = None, db: Session = Depends(get_db)):
    q = db.query(BlockRow)
    if block_id:
        q = q.filter_by(block_id=block_id)
    return q.order_by(BlockRow.block_id, BlockRow.row_number, BlockRow.side).all()


@router.get("/{row_id}", response_model=BlockRowRead)
def get_block_row(row_id: UUID, db: Session = Depends(get_db)):
    row = db.query(BlockRow).filter_by(id=row_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block row not found.")
    return row


@router.post("/", response_model=BlockRowRead, status_code=status.HTTP_201_CREATED)
def create_block_row(payload: BlockRowCreate, db: Session = Depends(get_db)):
    if payload.side is not None and payload.side not in VALID_SIDES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"side must be one of {sorted(VALID_SIDES)} or null.")
    if not db.query(Block).filter_by(id=payload.block_id).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found.")

    existing = db.query(BlockRow).filter_by(
        block_id=payload.block_id, row_number=payload.row_number, side=payload.side
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Row {payload.row_number}{payload.side or ''} already exists in this block.")

    row = BlockRow(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/{row_id}", response_model=BlockRowRead)
def update_block_row(row_id: UUID, payload: BlockRowUpdate, db: Session = Depends(get_db)):
    row = db.query(BlockRow).filter_by(id=row_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block row not found.")

    updates = payload.model_dump(exclude_none=True)

    if "side" in updates and updates["side"] is not None and updates["side"] not in VALID_SIDES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"side must be one of {sorted(VALID_SIDES)} or null.")

    new_row_number = updates.get("row_number", row.row_number)
    new_side = updates.get("side", row.side)
    if new_row_number != row.row_number or new_side != row.side:
        existing = db.query(BlockRow).filter_by(
            block_id=row.block_id, row_number=new_row_number, side=new_side
        ).first()
        if existing and existing.id != row.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Row {new_row_number}{new_side or ''} already exists in this block.")

    for key, value in updates.items():
        setattr(row, key, value)

    db.commit()
    db.refresh(row)
    return row


@router.delete("/{row_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block_row(row_id: UUID, db: Session = Depends(get_db)):
    row = db.query(BlockRow).filter_by(id=row_id).first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block row not found.")
    db.delete(row)
    db.commit()
