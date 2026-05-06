"""APScheduler 기반 자동 실행 스케줄러"""
import logging
import asyncio
from datetime import date
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import get_settings
from .database import SessionLocal

logger = logging.getLogger(__name__)
settings = get_settings()

scheduler = AsyncIOScheduler(timezone="UTC")


def _run_pipeline_job(market: str = "us"):
    from .services.report_generator import run_pipeline
    db = SessionLocal()
    try:
        logger.info(f"[Scheduler] collect_and_generate triggered market={market}")
        run_pipeline(db, date.today(), market=market)
    except Exception as e:
        logger.error(f"[Scheduler] Pipeline failed market={market}: {e}", exc_info=True)
        _notify_admin(f"[오류] 리포트 생성 실패({market}): {e}")
    finally:
        db.close()


async def _send_notifications_job(market: str = "us"):
    from .notifier import send_notifications
    db = SessionLocal()
    try:
        logger.info(f"[Scheduler] send_notifications triggered market={market}")
        sent = await send_notifications(db, date.today(), market=market)
        logger.info(f"[Scheduler] Sent {sent} notifications market={market}")
    except Exception as e:
        logger.error(f"[Scheduler] Notify failed market={market}: {e}", exc_info=True)
        _notify_admin(f"[오류] 알림 발송 실패({market}): {e}")
    finally:
        db.close()


def _health_check_job():
    from .database import engine
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        logger.debug("[Scheduler] Health check OK")
    except Exception as e:
        logger.error(f"[Scheduler] DB health check failed: {e}")
        _notify_admin(f"[경고] DB 연결 오류: {e}")


def _notify_admin(message: str):
    if not settings.telegram_bot_token or not settings.telegram_admin_chat_id:
        return
    import httpx
    try:
        httpx.post(
            f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
            json={"chat_id": settings.telegram_admin_chat_id, "text": message},
            timeout=5,
        )
    except Exception:
        pass


def start_scheduler():
    # US: KST 06:05 = UTC 21:05 전날
    scheduler.add_job(
        _run_pipeline_job,
        CronTrigger(
            hour=settings.schedule_collect_hour_utc,
            minute=settings.schedule_collect_minute_utc,
            timezone="UTC",
        ),
        id="collect_and_generate_us",
        replace_existing=True,
        kwargs={"market": "us"},
    )

    # US: KST 07:00 = UTC 22:00 전날
    scheduler.add_job(
        _send_notifications_job,
        CronTrigger(
            hour=settings.schedule_notify_hour_utc,
            minute=settings.schedule_notify_minute_utc,
            timezone="UTC",
        ),
        id="send_notifications_us",
        replace_existing=True,
        kwargs={"market": "us"},
    )

    # KR: KST 16:05 = UTC 07:05
    scheduler.add_job(
        _run_pipeline_job,
        CronTrigger(
            hour=settings.schedule_kr_collect_hour_utc,
            minute=settings.schedule_kr_collect_minute_utc,
            timezone="UTC",
        ),
        id="collect_and_generate_kr",
        replace_existing=True,
        kwargs={"market": "kr"},
    )

    # KR: KST 17:00 = UTC 08:00
    scheduler.add_job(
        _send_notifications_job,
        CronTrigger(
            hour=settings.schedule_kr_notify_hour_utc,
            minute=settings.schedule_kr_notify_minute_utc,
            timezone="UTC",
        ),
        id="send_notifications_kr",
        replace_existing=True,
        kwargs={"market": "kr"},
    )

    # 매시 정각 헬스체크
    scheduler.add_job(
        _health_check_job,
        CronTrigger(minute=0, timezone="UTC"),
        id="health_check",
        replace_existing=True,
    )

    scheduler.start()
    logger.info(
        "[Scheduler] Started — "
        "US collect@UTC %02d:%02d, US notify@UTC %02d:%02d | "
        "KR collect@UTC %02d:%02d, KR notify@UTC %02d:%02d" % (
            settings.schedule_collect_hour_utc, settings.schedule_collect_minute_utc,
            settings.schedule_notify_hour_utc, settings.schedule_notify_minute_utc,
            settings.schedule_kr_collect_hour_utc, settings.schedule_kr_collect_minute_utc,
            settings.schedule_kr_notify_hour_utc, settings.schedule_kr_notify_minute_utc,
        )
    )
