import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# ── API routes (must be registered BEFORE the SPA catch-all) ─────────────────
app.include_router(customers.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(analytics.router)
app.include_router(assistant.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api-info")
def api_info():
    return {"message": "ChaiSaathi AI Backend", "status": "running", "version": "1.0.0"}


# ── Static frontend serving ───────────────────────────────────────────────────
# In production, build.sh copies frontend/dist → backend/static
# STATIC_DIR resolves to  <repo>/backend/static
STATIC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "static"
)

if os.path.isdir(STATIC_DIR):
    # Mount /assets so Vite's hashed JS/CSS chunks are served efficiently
    assets_dir = os.path.join(STATIC_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_index():
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        SPA catch-all.
        1. Serve exact static files (favicon.svg, icons.svg, …) if they exist.
        2. Fall back to index.html so React Router handles the path.
        """
        candidate = os.path.join(STATIC_DIR, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))

else:
    # Local dev without a frontend build — just return a plain message
    @app.get("/")
    def root():
        return {"message": "ChaiSaathi AI Backend (dev mode)", "status": "running"}
