import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .scheduler import start_scheduler, scheduler
from .routers import reports, news, stocks, admin, subscribe
from .config import get_settings

logging.basicConfig(level=logging.INFO)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="AI Investment Report API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(reports.router)
app.include_router(news.router)
app.include_router(stocks.router)
app.include_router(admin.router)
app.include_router(subscribe.router)


@app.get("/api/v1/health")
def health():
    from .database import engine
    from sqlalchemy import text
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    scheduler_status = "running" if scheduler.running else "stopped"
    return {"status": "ok", "db": db_status, "scheduler": scheduler_status}
