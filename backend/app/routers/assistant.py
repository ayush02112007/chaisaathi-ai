from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
from ..database import get_db
from ..models import Sale, Expense, Udhaar, Customer, InventoryItem

router = APIRouter(prefix="/assistant", tags=["assistant"])


class ChatMessage(BaseModel):
    message: str
    language: str = "hi"  # hi or en


def get_business_context(db: Session) -> str:
    today = datetime.utcnow().date()
    month_ago = today - timedelta(days=30)

    today_sales = db.query(func.sum(Sale.amount)).filter(
        func.date(Sale.created_at) == today
    ).scalar() or 0

    month_sales = db.query(func.sum(Sale.amount)).filter(
        Sale.created_at >= month_ago
    ).scalar() or 0

    total_udhaar = db.query(func.sum(Udhaar.amount)).filter(
        Udhaar.is_paid == False
    ).scalar() or 0

    udhaar_customers = db.query(func.count(Customer.id)).join(
        Udhaar, Udhaar.customer_id == Customer.id
    ).filter(Udhaar.is_paid == False).scalar() or 0

    low_stock = db.query(InventoryItem).filter(
        InventoryItem.quantity <= InventoryItem.low_stock_alert
    ).all()
    low_stock_names = [i.name for i in low_stock]

    month_expenses = db.query(func.sum(Expense.amount)).filter(
        Expense.created_at >= month_ago
    ).scalar() or 0

    return f"""
Business Summary (as of {today}):
- Today's Sales: ₹{today_sales:.0f}
- This Month's Sales: ₹{month_sales:.0f}
- This Month's Expenses: ₹{month_expenses:.0f}
- Net Profit (30 days): ₹{month_sales - month_expenses:.0f}
- Total Outstanding Udhaar: ₹{total_udhaar:.0f} from {udhaar_customers} customers
- Low Stock Items: {', '.join(low_stock_names) if low_stock_names else 'None'}
"""


@router.post("/chat")
async def chat(msg: ChatMessage, db: Session = Depends(get_db)):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "response": "API key not set. Please add ANTHROPIC_API_KEY to .env file.",
            "language": msg.language
        }

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        context = get_business_context(db)

        system_prompt = f"""You are ChaiSaathi AI, a helpful business assistant for small Indian shop owners (dukandars).
You speak fluently in both Hindi and English. If the user writes in Hindi, respond in Hindi. If in English, respond in English.
You help with udhaar (credit) management, inventory, sales tracking, and business advice.
Keep responses concise and practical.

Current Business Data:
{context}"""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            system=system_prompt,
            messages=[{"role": "user", "content": msg.message}]
        )
        return {
            "response": response.content[0].text,
            "language": msg.language
        }
    except Exception as e:
        return {
            "response": f"Error: {str(e)}",
            "language": msg.language
        }
