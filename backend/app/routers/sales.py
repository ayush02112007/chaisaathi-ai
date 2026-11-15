from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
from ..database import get_db
from ..models import Sale, Expense, InventoryItem

router = APIRouter(prefix="/sales", tags=["sales"])


class SaleCreate(BaseModel):
    item_id: Optional[int] = None
    item_name: str = ""
    quantity: float = 1
    amount: float
    payment_mode: str = "cash"
    customer_id: Optional[int] = None
    notes: str = ""


class SaleOut(BaseModel):
    id: int
    item_id: Optional[int]
    item_name: str
    quantity: float
    amount: float
    payment_mode: str
    customer_id: Optional[int]
    notes: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseCreate(BaseModel):
    category: str = "General"
    amount: float
    description: str = ""


class ExpenseOut(BaseModel):
    id: int
    category: str
    amount: float
    description: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[SaleOut])
def list_sales(db: Session = Depends(get_db)):
    return db.query(Sale).order_by(Sale.created_at.desc()).limit(100).all()


@router.post("/", response_model=SaleOut)
def create_sale(data: SaleCreate, db: Session = Depends(get_db)):
    # Reduce inventory if item_id provided
    if data.item_id:
        item = db.query(InventoryItem).filter(InventoryItem.id == data.item_id).first()
        if item:
            item.quantity = max(0, item.quantity - data.quantity)
            if not data.item_name:
                data.item_name = item.name
    sale = Sale(**data.model_dump())
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.get("/expenses", response_model=List[ExpenseOut])
def list_expenses(db: Session = Depends(get_db)):
    return db.query(Expense).order_by(Expense.created_at.desc()).limit(100).all()


@router.post("/expenses", response_model=ExpenseOut)
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(**data.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    e = db.query(Expense).filter(Expense.id == expense_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(e)
    db.commit()
    return {"message": "Deleted"}
