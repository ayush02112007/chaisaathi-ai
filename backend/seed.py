"""
ChaiSaathi AI - Demo Data Seeder
Shop: Sharma Chai Corner, Delhi

Revenue target: ₹650-900/day  → ~₹22,000/month
Expense target: ₹6,000-7,000/month (operational only)
Net profit     : ~₹15,000/month

Safe: idempotent via sentinel phone. Never overwrites user data.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta, timezone, date
from app.database import SessionLocal, engine
from app.models import Base, Customer, Udhaar, InventoryItem, Sale, Expense
from sqlalchemy import func

Base.metadata.create_all(bind=engine)

SENTINEL_PHONE = "9876500001"


def ts(days_back, hour=10, minute=0):
    now = datetime.now(timezone.utc).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    return (now - timedelta(days=days_back)).replace(tzinfo=None)


def seed():
    db = SessionLocal()
    try:
        if db.query(Customer).filter(Customer.phone == SENTINEL_PHONE).first():
            print("✅ Demo data already present — skipping (no changes made).")
            return

        print("🌱 Seeding Sharma Chai Corner demo data...\n")

        # ── 1. CUSTOMERS (9) ─────────────────────────────────────────────────
        raw_customers = [
            ("Ramesh Kumar Sharma", SENTINEL_PHONE,  "12, Gandhi Nagar, Delhi"),
            ("Priya Verma",         "9876500002",    "Flat 3B, Laxmi Apartments"),
            ("Suresh Patel",        "9876500003",    "Shop 7, Main Bazaar"),
            ("Meena Devi",          "9876500004",    "House 45, Shastri Colony"),
            ("Ajay Singh",          "9876500005",    "Office Block A, Sector 5"),
            ("Kavita Gupta",        "9876500006",    "Near Govt School, Ward 12"),
            ("Mohit Yadav",         "9876500007",    "Auto Stand, Bus Depot Road"),
            ("Sunita Agarwal",      "9876500008",    "Plot 22, Nehru Vihar"),
            ("Deepak Chaudhary",    "9876500009",    "Kirana Shop, Lal Chowk"),
        ]

        C = {}
        for name, phone, addr in raw_customers:
            c = Customer(name=name, phone=phone, address=addr, created_at=ts(32, 9))
            db.add(c); db.flush(); C[name] = c
        print(f"  👤 {len(C)} customers created")

        # ── 2. INVENTORY (8 items) ────────────────────────────────────────────
        raw_inventory = [
            # (name, category, qty, unit, buy_price, sell_price, low_alert)
            ("Chai (Cutting)",           "Beverages", 180,  "cup",    3.0,  7.0,  30),
            ("Doodh (Milk)",             "Dairy",      22,  "litre", 52.0, 60.0,   5),
            ("Chai Patti (Brooke Bond)", "Grocery",   4.5,  "kg",   220.0,260.0,   1),
            ("Cheeni (Sugar)",           "Grocery",    15,  "kg",    42.0, 50.0,   3),
            ("Parle-G Biscuit",          "Snacks",     55,  "pkt",    5.0,  7.0,  15),
            ("Disposable Cups",          "Supplies",  450,  "pcs",    0.8,  1.5,  50),
            ("Paani Bottle (500ml)",     "Beverages",  28,  "bottle", 8.0, 15.0,  10),
            ("Namkeen (Mixed)",          "Snacks",     22,  "pkt",   10.0, 15.0,   5),
        ]

        I = {}
        for name, cat, qty, unit, bp, sp, alert in raw_inventory:
            item = InventoryItem(
                name=name, category=cat, quantity=qty, unit=unit,
                purchase_price=bp, selling_price=sp, low_stock_alert=alert,
                updated_at=ts(0)
            )
            db.add(item); db.flush(); I[name] = item
        print(f"  📦 {len(I)} inventory items created")

        # ── 3. SALES — build day-by-day for 30 days ───────────────────────────
        # Each day has a "batch" of transactions.
        # Morning rush: 40-60 chai cups cash
        # Afternoon: snacks, water, upi payments
        # Evening: chai batch, some udhaar for regulars
        # ~₹650-900 net per day

        def day_sales(d, chai_am, chai_pm, snack_qty, water_qty, milk_qty,
                      udhaar_cust=None, udhaar_chai=0, upi_cust=None):
            """Generate standard daily transactions."""
            txns = []
            # Morning chai (cash)
            if chai_am:
                txns.append((d, 8,  "Chai (Cutting)", chai_am, chai_am * 7, "cash", None, "Morning rush"))
            # Morning biscuits (cash)
            if snack_qty:
                txns.append((d, 9,  "Parle-G Biscuit", snack_qty, snack_qty * 7, "cash", None, ""))
            # Water bottles (cash/upi)
            if water_qty:
                txns.append((d, 11, "Paani Bottle (500ml)", water_qty, water_qty * 15, "cash", None, ""))
            # Afternoon namkeen
            txns.append((d, 13, "Namkeen (Mixed)", 2, 30, "upi" if upi_cust else "cash", upi_cust, ""))
            # Milk retail (upi)
            if milk_qty:
                txns.append((d, 14, "Doodh (Milk)", milk_qty, milk_qty * 60, "upi", upi_cust, ""))
            # Afternoon chai (upi)
            txns.append((d, 15, "Chai (Cutting)", 10, 70, "upi", upi_cust, "Afternoon"))
            # Evening chai batch (udhaar for regular or cash)
            if udhaar_cust and udhaar_chai:
                txns.append((d, 17, "Chai (Cutting)", udhaar_chai, udhaar_chai * 7, "udhaar", udhaar_cust, "Evening"))
            elif chai_pm:
                txns.append((d, 17, "Chai (Cutting)", chai_pm, chai_pm * 7, "cash", None, "Evening"))
            return txns

        all_sales = []

        # ── Weeks 3-4 (days 30-15): steady business ──────────────────────────
        week34 = [
            day_sales(30, 45, 12, 8, 4, 1, upi_cust="Priya Verma"),
            day_sales(29, 50, 10, 6, 3, 0),
            day_sales(28, 42, 14, 7, 5, 1, udhaar_cust="Suresh Patel", udhaar_chai=10),
            day_sales(27, 48, 12, 8, 4, 2, upi_cust="Meena Devi"),
            day_sales(26, 55, 10, 5, 3, 0),
            day_sales(25, 60, 15, 10, 6, 1, upi_cust="Priya Verma"),   # Sunday
            day_sales(24, 45, 10, 6, 4, 0, udhaar_cust="Ajay Singh", udhaar_chai=8),
            day_sales(23, 48, 12, 7, 5, 1),
            day_sales(22, 50, 10, 8, 4, 0),
            day_sales(21, 42, 14, 6, 3, 1, udhaar_cust="Ramesh Kumar Sharma", udhaar_chai=10),
            day_sales(20, 55, 12, 9, 5, 2, upi_cust="Sunita Agarwal"),
            day_sales(19, 50, 10, 7, 4, 0),
            day_sales(18, 48, 12, 6, 3, 1, upi_cust="Kavita Gupta"),
            day_sales(17, 45, 14, 8, 5, 0, udhaar_cust="Mohit Yadav", udhaar_chai=8),
            day_sales(16, 55, 10, 7, 4, 1),
        ]
        for group in week34:
            all_sales.extend(group)

        # ── Last 15 days (days 15-1): slightly busier ─────────────────────────
        week12 = [
            day_sales(15, 50, 12, 8, 5, 1, upi_cust="Priya Verma"),
            day_sales(14, 55, 10, 7, 4, 0, udhaar_cust="Deepak Chaudhary", udhaar_chai=10),
            day_sales(13, 48, 14, 8, 5, 1),
            day_sales(12, 60, 12, 9, 6, 2, upi_cust="Meena Devi"),
            day_sales(11, 65, 15, 10, 5, 0),    # peak day
            day_sales(10, 50, 10, 7, 4, 1, udhaar_cust="Suresh Patel", udhaar_chai=8),
            day_sales(9,  48, 12, 6, 3, 1, upi_cust="Priya Verma"),
            day_sales(8,  52, 12, 8, 5, 0, udhaar_cust="Mohit Yadav", udhaar_chai=6),
            day_sales(7,  55, 10, 7, 4, 1),
            day_sales(6,  50, 12, 6, 3, 0, udhaar_cust="Ramesh Kumar Sharma", udhaar_chai=8),
            day_sales(5,  58, 10, 8, 5, 2, upi_cust="Priya Verma"),
            day_sales(4,  55, 12, 7, 4, 1, udhaar_cust="Ajay Singh", udhaar_chai=10),
            day_sales(3,  65, 15, 9, 5, 1),     # weekend
            day_sales(2,  60, 12, 8, 4, 2, upi_cust="Sunita Agarwal"),
            day_sales(1,  70, 10, 10, 6, 3, udhaar_cust="Ramesh Kumar Sharma", udhaar_chai=8),
        ]
        for group in week12:
            all_sales.extend(group)

        # Today (partial day)
        all_sales.extend([
            (0, 8,  "Chai (Cutting)",       40, 280, "cash", None,         "Morning rush"),
            (0, 9,  "Parle-G Biscuit",       6,  42, "cash", None,         ""),
            (0, 10, "Paani Bottle (500ml)",   3,  45, "cash", None,         ""),
            (0, 11, "Chai (Cutting)",        10,  70, "upi",  "Ajay Singh", "Office order"),
        ])

        for d, h, iname, qty, amt, mode, cname, note in all_sales:
            item = I.get(iname)
            cust = C.get(cname) if cname else None
            db.add(Sale(
                item_id=item.id if item else None,
                item_name=iname, quantity=qty, amount=float(amt),
                payment_mode=mode, customer_id=cust.id if cust else None,
                notes=note, created_at=ts(d, h)
            ))

        print(f"  🛒 {len(all_sales)} sales transactions added")

        # ── 4. UDHAAR ENTRIES (16 entries, mix of paid & pending) ─────────────
        raw_udhaar = [
            # (cust, amount, description, days_created, is_paid, days_paid)
            ("Ramesh Kumar Sharma",  70,  "10 chai (day-21 eve)",   21, True,  18),
            ("Ramesh Kumar Sharma",  56,  "8 chai (day-6 eve)",      6, False, None),
            ("Ramesh Kumar Sharma",  56,  "8 chai (yesterday)",      1, False, None),
            ("Suresh Patel",         70,  "10 chai (day-28)",       28, True,  23),
            ("Suresh Patel",         56,  "8 chai (day-10)",        10, False, None),
            ("Mohit Yadav",          56,  "8 chai (day-17)",        17, True,  13),
            ("Mohit Yadav",          42,  "6 chai (day-8)",          8, False, None),
            ("Mohit Yadav",          42,  "6 chai (day-5 extra)",    5, False, None),
            ("Deepak Chaudhary",     70,  "10 chai (day-14)",       14, True,   9),
            ("Deepak Chaudhary",     56,  "Chai + snacks (day-3)",   3, False, None),
            ("Ajay Singh",          140,  "Office order week 4",    24, True,  18),
            ("Ajay Singh",           70,  "10 chai (day-4)",         4, False, None),
            ("Kavita Gupta",         84,  "Chai month",             22, True,  17),
            ("Kavita Gupta",         42,  "6 chai (day-7)",          7, False, None),
            ("Meena Devi",           60,  "Chai + sugar",           20, True,  15),
            ("Priya Verma",          48,  "Chai this week",          3, False, None),
        ]

        for cname, amt, desc, d_c, paid, d_p in raw_udhaar:
            db.add(Udhaar(
                customer_id=C[cname].id, amount=float(amt), description=desc,
                is_paid=paid, created_at=ts(d_c, 18),
                paid_at=ts(d_p, 11) if paid else None
            ))

        paid_c   = sum(1 for *_, p, _ in raw_udhaar if p)
        unpaid_c = len(raw_udhaar) - paid_c
        print(f"  📒 {len(raw_udhaar)} udhaar entries ({paid_c} paid, {unpaid_c} pending)")

        # ── 5. EXPENSES — operational only (no COGS, since revenue captures margin) ──
        # ~₹6,500/month → ₹216/day
        raw_expenses = [
            # (category, amount, description, days_back)
            ("Raw Material",  1100, "Chai patti 5kg (Brooke Bond)",      28),
            ("Raw Material",   420, "Cheeni 10kg",                        26),
            ("Supplies",       400, "Disposable cups 500 pcs",            22),
            ("Utilities",      380, "Electricity bill",                   20),
            ("Raw Material",   420, "Cheeni 10kg restock",                17),
            ("Supplies",       180, "Gas cylinder refill",                14),
            ("Raw Material",  1100, "Chai patti 5kg restock",             12),
            ("Supplies",       400, "Disposable cups 500 pcs",             9),
            ("Maintenance",    350, "Stove service + parts",               6),
            ("Raw Material",   420, "Cheeni 10kg restock",                 5),
            ("Utilities",      150, "Water & misc",                        4),
            ("Raw Material",   550, "Chai patti 2.5kg (mid-month)",        2),
            ("Supplies",       180, "Gas cylinder refill",                 1),
            ("Supplies",        90, "Spoons, napkins, misc supplies",      0),
        ]

        for cat, amt, desc, d in raw_expenses:
            db.add(Expense(
                category=cat, amount=float(amt),
                description=desc, created_at=ts(d, 9)
            ))

        print(f"  💸 {len(raw_expenses)} expense entries added")

        db.commit()

        # ── 6. VERIFICATION ───────────────────────────────────────────────────
        today_dt   = date.today()
        month_ago  = today_dt - timedelta(days=30)

        month_rev  = db.query(func.sum(Sale.amount)).filter(
                        Sale.created_at >= month_ago).scalar() or 0
        month_exp  = db.query(func.sum(Expense.amount)).filter(
                        Expense.created_at >= month_ago).scalar() or 0
        pend_udh   = db.query(func.sum(Udhaar.amount)).filter(
                        Udhaar.is_paid == False).scalar() or 0
        today_rev  = db.query(func.sum(Sale.amount)).filter(
                        func.date(Sale.created_at) == today_dt).scalar() or 0
        week_rev   = db.query(func.sum(Sale.amount)).filter(
                        Sale.created_at >= today_dt - timedelta(days=7)).scalar() or 0

        # Per-day trend check
        print(f"""
✅ Seed complete! Sharma Chai Corner is ready.

📊 Database Summary:
   Customers       : {db.query(Customer).count()}
   Inventory items : {db.query(InventoryItem).count()}
   Sales records   : {db.query(Sale).count()}
   Udhaar entries  : {db.query(Udhaar).count()}
   Expenses        : {db.query(Expense).count()}

💰 Financial Snapshot (what dashboard will show):
   Today's Sales   : ₹{today_rev:.0f}
   This Week Sales : ₹{week_rev:.0f}
   30-day Revenue  : ₹{month_rev:.0f}
   30-day Expenses : ₹{month_exp:.0f}
   Net Profit (30d): ₹{month_rev - month_exp:.0f}  {'✅ Positive' if month_rev > month_exp else '⚠️  Negative'}
   Pending Udhaar  : ₹{pend_udh:.0f}
""")

        # Day-by-day last 7 days
        print("  📅 Last 7 days sales (dashboard trend):")
        for i in range(6, -1, -1):
            d = today_dt - timedelta(days=i)
            amt = db.query(func.sum(Sale.amount)).filter(
                      func.date(Sale.created_at) == d).scalar() or 0
            bar = "█" * int(amt / 50)
            print(f"     {d}  ₹{amt:>6.0f}  {bar}")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seed failed: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
