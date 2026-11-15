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


def _friendly_error(e: Exception, language: str) -> str:
    """Return a user-friendly error message without exposing internals or the key."""
    err = str(e)
    is_hindi = language == "hi"

    if "401" in err or "authentication_error" in err or "invalid x-api-key" in err:
        return (
            "API key galat hai ya expire ho gaya hai. "
            "Render dashboard mein ANTHROPIC_API_KEY dobara check karein. 🔑"
            if is_hindi else
            "The Anthropic API key is invalid or expired. "
            "Please verify ANTHROPIC_API_KEY in the Render environment settings."
        )
    if "429" in err or "rate_limit" in err or "overloaded" in err:
        return (
            "Abhi bahut zyada requests aa rahi hain. Thodi der baad try karein. 🙏"
            if is_hindi else
            "Too many requests right now. Please try again in a moment."
        )
    if "404" in err or "not_found_error" in err:
        return (
            "AI model available nahi hai. Admin se contact karein. ⚙️"
            if is_hindi else
            "The AI model is unavailable. Please contact the admin."
        )
    if "timeout" in err.lower() or "connect" in err.lower():
        return (
            "Network error aaya. Internet connection check karein aur dobara try karein. 🌐"
            if is_hindi else
            "Network error. Please check your connection and try again."
        )
    # Generic — don't leak internal detail
    return (
        "Kuch technical problem aayi. Thodi der baad dobara try karein. 🛠️"
        if is_hindi else
        "A technical error occurred. Please try again shortly."
    )


@router.post("/chat")
async def chat(msg: ChatMessage, db: Session = Depends(get_db)):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_key_here":
        return {
            "response": (
                "AI assistant ke liye ANTHROPIC_API_KEY set nahi hai. "
                "Render dashboard → Environment mein key add karein. "
                "Baaki sabhi features bina key ke kaam karte hain! 🙏"
            ),
            "language": msg.language
        }

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        context = get_business_context(db)

        system_prompt = f"""You are ChaiSaathi AI, a helpful business assistant for small Indian shop owners (dukandars).
You speak fluently in both Hindi and English. If the user writes in Hindi or Hinglish, respond in Hindi. If in English, respond in English.
You help with udhaar (credit) management, inventory, sales tracking, and business advice.
Keep responses concise (2-4 sentences) and practical. Use ₹ for currency.

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
            "response": _friendly_error(e, msg.language),
            "language": msg.language
        }


@router.get("/status")
def assistant_status():
    """Check if AI assistant is configured — does NOT reveal the key value."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    configured = bool(api_key) and api_key != "your_key_here"
    return {
        "configured": configured,
        "hint": "Set ANTHROPIC_API_KEY in Render environment variables" if not configured else None
    }
