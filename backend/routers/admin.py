from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import get_settings
from ..services.report_generator import run_pipeline
from ..notifier import send_notifications

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
settings = get_settings()


def verify_admin(x_admin_key: str = Header(...)):
    if x_admin_key != settings.admin_secret_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")


@router.post("/generate")
def trigger_generate(
    report_date: date = None,
    market: str = "us",
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin),
):
    if report_date is None:
        report_date = date.today()
    if market not in ("us", "kr"):
        raise HTTPException(status_code=400, detail="market must be 'us' or 'kr'")
    try:
        report = run_pipeline(db, report_date, market=market)
        return {"status": "success", "report_date": str(report.date), "market": market, "id": report.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notify")
async def trigger_notify(
    report_date: date = None,
    market: str = "us",
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin),
):
    if report_date is None:
        report_date = date.today()
    if market not in ("us", "kr"):
        raise HTTPException(status_code=400, detail="market must be 'us' or 'kr'")
    try:
        sent = await send_notifications(db, report_date, market=market)
        return {"status": "success", "market": market, "sent_count": sent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
