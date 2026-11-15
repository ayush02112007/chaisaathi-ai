from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import customers, inventory, sales, analytics, assistant

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ChaiSaathi AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(analytics.router)
app.include_router(assistant.router)


@app.get("/")
def root():
    return {"message": "ChaiSaathi AI Backend", "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}
