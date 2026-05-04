from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from ..models import Subscriber
from ..schemas import SubscribeRequest, SubscribeResponse

router = APIRouter(prefix="/api/v1/subscribe", tags=["subscribe"])


@router.post("", response_model=SubscribeResponse)
def subscribe(req: SubscribeRequest, db: Session = Depends(get_db)):
    if req.type not in ("telegram", "email"):
        raise HTTPException(status_code=400, detail="type must be 'telegram' or 'email'")
    try:
        sub = db.query(Subscriber).filter(Subscriber.contact == req.contact).first()
        if sub:
            sub.is_active = 1
            db.commit()
            return SubscribeResponse(success=True, message="구독이 재활성화되었습니다.")
        new_sub = Subscriber(type=req.type, contact=req.contact, is_active=1)
        db.add(new_sub)
        db.commit()
        return SubscribeResponse(success=True, message="구독이 완료되었습니다.")
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already subscribed")


@router.delete("", response_model=SubscribeResponse)
def unsubscribe(contact: str, db: Session = Depends(get_db)):
    sub = db.query(Subscriber).filter(Subscriber.contact == contact).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscriber not found")
    sub.is_active = 0
    db.commit()
    return SubscribeResponse(success=True, message="구독이 해제되었습니다.")
