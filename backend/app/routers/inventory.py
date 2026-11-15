from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..database import get_db
from ..models import InventoryItem

router = APIRouter(prefix="/inventory", tags=["inventory"])


class ItemCreate(BaseModel):
    name: str
    category: str = "General"
    quantity: float = 0
    unit: str = "pcs"
    purchase_price: float = 0
    selling_price: float = 0
    low_stock_alert: float = 10


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    purchase_price: Optional[float] = None
    selling_price: Optional[float] = None
    low_stock_alert: Optional[float] = None


class ItemOut(BaseModel):
    id: int
    name: str
    category: str
    quantity: float
    unit: str
    purchase_price: float
    selling_price: float
    low_stock_alert: float
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ItemOut])
def list_items(db: Session = Depends(get_db)):
    return db.query(InventoryItem).all()


@router.get("/low-stock", response_model=List[ItemOut])
def low_stock(db: Session = Depends(get_db)):
    return db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.low_stock_alert
    ).all()


@router.post("/", response_model=ItemOut)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    item = InventoryItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, data: ItemUpdate, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"message": "Deleted"}
