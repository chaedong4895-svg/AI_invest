from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# ── News ──────────────────────────────────────────────────────────────────────

class NewsSchema(BaseModel):
    id: int
    report_date: date
    title: str
    summary: str
    sentiment: str
    sector: Optional[str]
    source: Optional[str]
    url: Optional[str]
    published_at: Optional[datetime]
    order_index: int

    class Config:
        from_attributes = True


# ── Stock ─────────────────────────────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    news: int = 0
    sector: int = 0
    price: int = 0
    volume: int = 0
    technical: int = 0
    volatility: int = 0
    event: int = 0


class StockSchema(BaseModel):
    id: int
    report_date: date
    rank: int
    ticker: str
    company_name: str
    score: int
    score_breakdown: Optional[dict]
    reason: str
    risk_factor: str
    buy_price: float
    target_price: float
    stop_price: float

    class Config:
        from_attributes = True


# ── Report ────────────────────────────────────────────────────────────────────

class MarketSummary(BaseModel):
    nasdaq: float
    sp500: float
    dow: float
    russell: float
    vix: float
    tnx: float


class SectorItem(BaseModel):
    ticker: str
    name: str
    change_pct: float


class SectorAnalysis(BaseModel):
    top3_bullish: list[SectorItem] = []
    top3_bearish: list[SectorItem] = []
    etf_changes: dict = {}


class ReportSchema(BaseModel):
    id: int
    date: date
    market: str = "us"
    risk_level: str
    market_summary: dict
    sector_analysis: Optional[dict]
    risk_warning: Optional[str]
    report_version: int
    created_at: datetime
    news_items: list[NewsSchema] = []
    stocks: list[StockSchema] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class ReportSummary(BaseModel):
    date: date
    market: str = "us"
    risk_level: str
    market_summary: dict
    created_at: datetime

    class Config:
        from_attributes = True


# ── Subscriber ────────────────────────────────────────────────────────────────

class SubscribeRequest(BaseModel):
    type: str   # telegram / email
    contact: str


class SubscribeResponse(BaseModel):
    success: bool
    message: str


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    db: str
    scheduler: str
