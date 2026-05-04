from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, func
from sqlalchemy import JSON as JSONB
from .database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True)
    market = Column(String(5), nullable=False, default="us")  # us / kr
    risk_level = Column(String(10), nullable=False)
    market_summary = Column(JSONB, nullable=False)
    sector_analysis = Column(JSONB)
    risk_warning = Column(Text)
    report_version = Column(Integer, default=1)
    created_at = Column(DateTime, nullable=False, default=func.now())


class NewsItem(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Date, nullable=False, index=True)
    report_market = Column(String(5), nullable=False, default="us")
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    sentiment = Column(String(10), nullable=False)
    sector = Column(String(50))
    source = Column(String(50))
    url = Column(Text)
    published_at = Column(DateTime)
    order_index = Column(Integer, nullable=False)


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Date, nullable=False, index=True)
    report_market = Column(String(5), nullable=False, default="us")
    rank = Column(Integer, nullable=False)
    ticker = Column(String(10), nullable=False)
    company_name = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    score_breakdown = Column(JSONB)
    reason = Column(Text, nullable=False)
    risk_factor = Column(Text, nullable=False)
    buy_price = Column(Numeric(12, 0), nullable=False)   # KRW는 소수점 없음
    target_price = Column(Numeric(12, 0), nullable=False)
    stop_price = Column(Numeric(12, 0), nullable=False)
    raw_data = Column(JSONB)


class Subscriber(Base):
    __tablename__ = "subscribers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(10), nullable=False)
    contact = Column(String(200), nullable=False, unique=True)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, nullable=False, default=func.now())


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(Date, nullable=False)
    type = Column(String(10), nullable=False)
    contact = Column(String(200), nullable=False)
    status = Column(String(10), nullable=False)
    error_msg = Column(Text)
    sent_at = Column(DateTime, nullable=False, default=func.now())
