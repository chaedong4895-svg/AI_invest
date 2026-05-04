from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import NewsItem
from ..schemas import NewsSchema

router = APIRouter(prefix="/api/v1/news", tags=["news"])


@router.get("/{report_date}", response_model=list[NewsSchema])
def get_news_by_date(
    report_date: date,
    market: str = Query("us"),
    db: Session = Depends(get_db),
):
    items = (
        db.query(NewsItem)
        .filter(NewsItem.report_date == report_date, NewsItem.report_market == market)
        .order_by(NewsItem.order_index)
        .all()
    )
    if not items:
        raise HTTPException(status_code=404, detail=f"No news for {report_date} market={market}")
    return items
