from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Stock
from ..schemas import StockSchema

router = APIRouter(prefix="/api/v1/stocks", tags=["stocks"])


@router.get("/{report_date}", response_model=list[StockSchema])
def get_stocks_by_date(
    report_date: date,
    market: str = Query("us"),
    db: Session = Depends(get_db),
):
    stocks = (
        db.query(Stock)
        .filter(Stock.report_date == report_date, Stock.report_market == market)
        .order_by(Stock.rank)
        .all()
    )
    if not stocks:
        raise HTTPException(status_code=404, detail=f"No stocks for {report_date} market={market}")
    return stocks


@router.get("/{report_date}/{ticker}", response_model=StockSchema)
def get_stock_detail(
    report_date: date,
    ticker: str,
    market: str = Query("us"),
    db: Session = Depends(get_db),
):
    stock = (
        db.query(Stock)
        .filter(
            Stock.report_date == report_date,
            Stock.report_market == market,
            Stock.ticker == ticker,
        )
        .first()
    )
    if not stock:
        raise HTTPException(status_code=404, detail=f"{ticker} not found for {report_date}")
    return stock
