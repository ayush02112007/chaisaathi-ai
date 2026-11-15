from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    address = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    udhaar_entries = relationship("Udhaar", back_populates="customer")


class Udhaar(Base):
    __tablename__ = "udhaar"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    amount = Column(Float, nullable=False)
    description = Column(String, default="")
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    customer = relationship("Customer", back_populates="udhaar_entries")


class InventoryItem(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, default="General")
    quantity = Column(Float, default=0)
    unit = Column(String, default="pcs")
    purchase_price = Column(Float, default=0)
    selling_price = Column(Float, default=0)
    low_stock_alert = Column(Float, default=10)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory.id"), nullable=True)
    item_name = Column(String, default="")
    quantity = Column(Float, default=1)
    amount = Column(Float, nullable=False)
    payment_mode = Column(String, default="cash")  # cash, upi, udhaar
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    notes = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Expense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, default="General")
    amount = Column(Float, nullable=False)
    description = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
