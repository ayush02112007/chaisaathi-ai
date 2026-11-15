from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Sale, Expense, Udhaar, Customer, InventoryItem

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # Today's sales
    today_sales = db.query(func.sum(Sale.amount)).filter(
        func.date(Sale.created_at) == today
    ).scalar() or 0

    # This week's sales
    week_sales = db.query(func.sum(Sale.amount)).filter(
        Sale.created_at >= week_ago
    ).scalar() or 0

    # This month's sales
    month_sales = db.query(func.sum(Sale.amount)).filter(
        Sale.created_at >= month_ago
    ).scalar() or 0

    # Total expenses this month
    month_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.created_at >= month_ago
    ).scalar() or 0

    # Total outstanding udhaar
    total_udhaar = db.query(func.sum(Udhaar.amount)).filter(
        Udhaar.is_paid == False
    ).scalar() or 0

    # Customer count
    customer_count = db.query(func.count(Customer.id)).scalar() or 0

    # Low stock count
    low_stock_count = db.query(func.count(InventoryItem.id)).filter(
        InventoryItem.quantity <= InventoryItem.low_stock_alert
    ).scalar() or 0

    # Last 7 days sales trend
    trend = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        amt = db.query(func.sum(Sale.amount)).filter(
            func.date(Sale.created_at) == d
        ).scalar() or 0
        trend.append({"date": str(d), "sales": float(amt)})

    # Payment mode breakdown (last 30 days)
    payment_modes = db.query(Sale.payment_mode, func.sum(Sale.amount)).filter(
        Sale.created_at >= month_ago
    ).group_by(Sale.payment_mode).all()
    payment_breakdown = [{"mode": m, "amount": float(a)} for m, a in payment_modes]

    # Expense categories
    expense_cats = db.query(Expense.category, func.sum(Expense.amount)).filter(
        Expense.created_at >= month_ago
    ).group_by(Expense.category).all()
    expense_breakdown = [{"category": c, "amount": float(a)} for c, a in expense_cats]

    return {
        "today_sales": float(today_sales),
        "week_sales": float(week_sales),
        "month_sales": float(month_sales),
        "month_expenses": float(month_expenses),
        "net_profit": float(month_sales - month_expenses),
        "total_udhaar": float(total_udhaar),
        "customer_count": int(customer_count),
        "low_stock_count": int(low_stock_count),
        "sales_trend": trend,
        "payment_breakdown": payment_breakdown,
        "expense_breakdown": expense_breakdown,
    }
