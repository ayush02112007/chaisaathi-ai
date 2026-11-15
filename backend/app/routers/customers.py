from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from ..database import get_db
from ..models import Customer, Udhaar

router = APIRouter(prefix="/customers", tags=["customers"])


class CustomerCreate(BaseModel):
    name: str
    phone: str
    address: str = ""


class CustomerOut(BaseModel):
    id: int
    name: str
    phone: str
    address: str
    created_at: datetime
    total_udhaar: float = 0

    class Config:
        from_attributes = True


class UdhaarCreate(BaseModel):
    customer_id: int
    amount: float
    description: str = ""


class UdhaarOut(BaseModel):
    id: int
    customer_id: int
    amount: float
    description: str
    is_paid: bool
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[CustomerOut])
def list_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    result = []
    for c in customers:
        total = db.query(func.sum(Udhaar.amount)).filter(
            Udhaar.customer_id == c.id, Udhaar.is_paid == False
        ).scalar() or 0
        out = CustomerOut(
            id=c.id, name=c.name, phone=c.phone,
            address=c.address, created_at=c.created_at, total_udhaar=total
        )
        result.append(out)
    return result


@router.post("/", response_model=CustomerOut)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Customer with this phone already exists")
    c = Customer(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return CustomerOut(id=c.id, name=c.name, phone=c.phone, address=c.address,
                       created_at=c.created_at, total_udhaar=0)


@router.get("/{customer_id}/udhaar", response_model=List[UdhaarOut])
def get_udhaar(customer_id: int, db: Session = Depends(get_db)):
    return db.query(Udhaar).filter(Udhaar.customer_id == customer_id).all()


@router.post("/udhaar", response_model=UdhaarOut)
def add_udhaar(data: UdhaarCreate, db: Session = Depends(get_db)):
    u = Udhaar(**data.model_dump())
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.put("/udhaar/{udhaar_id}/pay")
def mark_paid(udhaar_id: int, db: Session = Depends(get_db)):
    u = db.query(Udhaar).filter(Udhaar.id == udhaar_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    u.is_paid = True
    u.paid_at = datetime.utcnow()
    db.commit()
    return {"message": "Marked as paid"}


@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(c)
    db.commit()
    return {"message": "Deleted"}
