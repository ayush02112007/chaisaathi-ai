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


def _classify_error(e: Exception) -> tuple[str, str]:
    """
    Return (en_message, hi_message) for the given exception.
    Uses isinstance checks (robust) before falling back to string matching.
    Never exposes the API key or raw error internals.
    """
    try:
        import anthropic as _sdk

        # ── Authentication / credentials ──────────────────────────────────
        if isinstance(e, (_sdk.AuthenticationError, _sdk.CredentialsError)):
            return (
                "The Anthropic API key is invalid or expired. "
                "Please replace ANTHROPIC_API_KEY in Render Environment Variables.",
                "API key galat hai ya expire ho gaya hai. "
                "Render dashboard mein ANTHROPIC_API_KEY dobara update karein. 🔑"
            )

        # ── Account / billing issues ──────────────────────────────────────
        if isinstance(e, _sdk.PermissionDeniedError):
            return (
                "API key does not have permission for this model or feature. "
                "Check your Anthropic account plan at console.anthropic.com.",
                "Is API key ko is model ka permission nahi hai. "
                "console.anthropic.com par apna account check karein. 🔒"
            )
        if isinstance(e, (_sdk.OrganizationOnHoldError,
                          _sdk.OrganizationTypeNotSupportedError)):
            return (
                "Your Anthropic account is on hold or pending verification. "
                "Visit console.anthropic.com to complete account setup.",
                "Aapka Anthropic account hold par hai. "
                "console.anthropic.com par account setup poora karein. ⚠️"
            )
        if isinstance(e, _sdk.EnforcedSpendLimitReachedError):
            return (
                "API spend limit reached. Add credits at console.anthropic.com.",
                "API credits khatam ho gaye hain. "
                "console.anthropic.com par credits add karein. 💳"
            )

        # ── Rate limits ───────────────────────────────────────────────────
        if isinstance(e, (_sdk.RateLimitError, _sdk.OverloadedError,
                          _sdk.RampLimitExceededError)):
            return (
                "Too many requests right now. Please try again in a moment.",
                "Abhi bahut zyada requests aa rahi hain. "
                "Thodi der baad try karein. 🙏"
            )

        # ── Model / request errors ────────────────────────────────────────
        if isinstance(e, _sdk.NotFoundError):
            return (
                "The AI model was not found. "
                "Contact the admin to update the model name.",
                "AI model nahi mila. Admin se model name update karne ko karein. 🔧"
            )
        if isinstance(e, _sdk.BadRequestError):
            return (
                "Invalid request sent to Anthropic API. "
                "Check model name and request format.",
                "Anthropic API par galat request gayi. "
                "Model name aur request format check karein. ⚙️"
            )

        # ── Network / timeout ─────────────────────────────────────────────
        if isinstance(e, (_sdk.APIConnectionError, _sdk.APITimeoutError,
                          _sdk.RequestTimeoutError, _sdk.GatewayTimeoutError,
                          _sdk.DeadlineExceededError)):
            return (
                "Network timeout. Please check connectivity and try again.",
                "Network timeout aaya. "
                "Internet connection check karein aur dobara try karein. 🌐"
            )

        # ── Server errors ─────────────────────────────────────────────────
        if isinstance(e, _sdk.InternalServerError):
            return (
                "Anthropic servers are experiencing an issue. Try again shortly.",
                "Anthropic servers mein problem hai. Thodi der baad try karein. 🛠️"
            )

    except ImportError:
        pass

    # Last-resort generic — still no key exposure
    return (
        "A temporary error occurred. Please try again shortly.",
        "Kuch technical problem aayi. Thodi der baad dobara try karein. 🛠️"
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
            messages=[{"role": "user", "content": [{"type": "text", "text": msg.message}]}]
        )
        # Extract text safely — handle both TextBlock and plain string content
        content = response.content[0]
        text = content.text if hasattr(content, "text") else str(content)
        return {"response": text, "language": msg.language}

    except Exception as e:
        en_msg, hi_msg = _classify_error(e)
        return {
            "response": hi_msg if msg.language == "hi" else en_msg,
            "language": msg.language
        }


@router.get("/status")
def assistant_status():
    """Check configuration and diagnose last error — never reveals key value."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    configured = bool(api_key) and api_key != "your_key_here"

    # Basic key format check (safe — just checks prefix/length, not value)
    key_format_ok = None
    if configured:
        key_format_ok = api_key.startswith("sk-ant-") and len(api_key) > 40

    return {
        "configured": configured,
        "key_format_valid": key_format_ok,
        "hint": (
            None if configured else
            "Set ANTHROPIC_API_KEY in Render environment variables"
        ),
        "format_hint": (
            None if key_format_ok else
            "Key should start with 'sk-ant-' and be longer than 40 chars"
        ) if configured else None
    }


@router.get("/debug-error")
async def debug_error(db: Session = Depends(get_db)):
    """
    Makes a real API call and returns only the exception class name —
    never the message (which could contain account details).
    Use this to diagnose production errors without exposing secrets.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_key_here":
        return {"error_class": None, "configured": False}

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=5,
            messages=[{"role": "user", "content": [{"type": "text", "text": "hi"}]}]
        )
        content = response.content[0]
        text = content.text if hasattr(content, "text") else str(content)
        return {
            "error_class": None,
            "success": True,
            "response_preview": text[:30],
            "model": response.model,
            "stop_reason": response.stop_reason
        }
    except Exception as e:
        return {
            "error_class": type(e).__name__,
            "error_module": type(e).__module__,
            "success": False,
            # status_code if present — safe, it's just an HTTP status number
            "status_code": getattr(e, "status_code", None)
        }
