from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Report, NewsItem, Stock
from ..schemas import ReportSchema, ReportSummary

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


def _attach(report: Report, db: Session) -> Report:
    """news_items / stocks를 report 객체에 동적으로 붙임"""
    report.news_items = (
        db.query(NewsItem)
        .filter(NewsItem.report_date == report.date, NewsItem.report_market == report.market)
        .order_by(NewsItem.order_index)
        .all()
    )
    report.stocks = (
        db.query(Stock)
        .filter(Stock.report_date == report.date, Stock.report_market == report.market)
        .order_by(Stock.rank)
        .all()
    )
    return report


@router.get("/latest", response_model=ReportSchema)
def get_latest_report(market: str = Query("us"), db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .filter(Report.market == market)
        .order_by(Report.date.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="No reports found")
    return _attach(report, db)


@router.get("/{report_date}", response_model=ReportSchema)
def get_report_by_date(report_date: date, market: str = Query("us"), db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .filter(Report.date == report_date, Report.market == market)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail=f"No report for {report_date} market={market}")
    return _attach(report, db)


@router.get("", response_model=list[ReportSummary])
def list_reports(
    market: str = Query("us"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit
    return (
        db.query(Report)
        .filter(Report.market == market)
        .order_by(Report.date.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
