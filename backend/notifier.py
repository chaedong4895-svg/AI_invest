"""텔레그램 Bot 및 SendGrid 이메일 알림 발송"""
import logging
from datetime import date
import httpx
from sqlalchemy.orm import Session

from .config import get_settings
from .models import Report, Stock, Subscriber, NotificationLog

logger = logging.getLogger(__name__)
settings = get_settings()

RISK_EMOJI = {"Risk-On": "🟢", "Neutral": "🟡", "Risk-Off": "🔴"}
RISK_MSG = {
    "Risk-On": "적극 매수 고려 가능",
    "Neutral": "선별적 접근 권고",
    "Risk-Off": "현금 비중 확대 고려",
}


async def send_notifications(db: Session, report_date: date, market: str = "us") -> int:
    report = db.query(Report).filter(
        Report.date == report_date,
        Report.market == market,
    ).first()
    if not report:
        logger.warning(f"No report found for {report_date} / {market}")
        return 0

    stocks = (
        db.query(Stock)
        .filter(Stock.report_date == report_date, Stock.report_market == market)
        .order_by(Stock.rank)
        .all()
    )

    # 구독자 목록 + 어드민 채팅 ID를 항상 포함
    subscribers = db.query(Subscriber).filter(Subscriber.is_active == 1).all()
    targets = list(subscribers)

    admin_id = settings.telegram_admin_chat_id
    if admin_id and not any(s.contact == admin_id and s.type == "telegram" for s in subscribers):
        from types import SimpleNamespace
        targets.append(SimpleNamespace(type="telegram", contact=admin_id))

    sent = 0
    for sub in targets:
        success = False
        error_msg = None
        try:
            if sub.type == "telegram":
                msg = _build_telegram_message(report, stocks, market)
                await _send_telegram(sub.contact, msg)
                success = True
            elif sub.type == "email":
                html = _build_email_html(report, stocks, market)
                await _send_email(sub.contact, f"📈 AI 투자 리포트 — {report_date}", html)
                success = True
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Notify failed [{sub.contact}]: {e}")

        if hasattr(sub, "id"):  # DB 구독자만 로그 기록
            db.add(NotificationLog(
                report_date=report_date,
                type=sub.type,
                contact=sub.contact,
                status="sent" if success else "failed",
                error_msg=error_msg,
            ))
        if success:
            sent += 1

    db.commit()
    return sent


def _build_telegram_message(report: Report, stocks: list[Stock], market: str = "us") -> str:
    m = report.market_summary
    emoji = RISK_EMOJI.get(report.risk_level, "🟡")
    msg_text = RISK_MSG.get(report.risk_level, "")
    is_kr = (market == "kr")
    flag = "🇰🇷" if is_kr else "🇺🇸"

    lines = [
        f"📈 AI 투자 리포트 {flag} — {report.date}",
        f"{emoji} 시장 상태: {report.risk_level} — {msg_text}",
        "",
    ]

    if is_kr:
        lines += [
            "📊 한국 시장",
            f"• KOSPI: {m.get('kospi_value', 0):,.2f} ({_fmt_pct(m.get('kospi', 0))})",
            f"• KOSDAQ: {m.get('kosdaq_value', 0):,.2f} ({_fmt_pct(m.get('kosdaq', 0))})",
            f"• USD/KRW: {m.get('usd_krw_value', 0):.0f}원 ({_fmt_pct(m.get('usd_krw', 0))})",
            f"• VIX: {m.get('vix', 20):.1f}",
        ]
    else:
        lines += [
            "📊 미국 시장",
            f"• Nasdaq: {_fmt_pct(m.get('nasdaq', 0))}",
            f"• S&P500: {_fmt_pct(m.get('sp500', 0))}",
            f"• VIX: {m.get('vix', 20):.1f}",
            f"• 10Y: {m.get('tnx', 4.3):.2f}%",
        ]

    if report.sector_analysis and report.sector_analysis.get("top3_bullish"):
        bullish = report.sector_analysis["top3_bullish"][:2]
        bearish = report.sector_analysis["top3_bearish"][:1]
        s_parts = [f"{b['name']}({_fmt_pct(b['change_pct'])})" for b in bullish]
        lines.append(f"\n🔥 강세 섹터: {' | '.join(s_parts)}")
        if bearish:
            lines.append(f"❄️ 약세 섹터: {bearish[0]['name']}({_fmt_pct(bearish[0]['change_pct'])})")

    if stocks:
        lines.append("\n⭐ 추천 종목 Top 5")
        for s in stocks:
            ticker = s.ticker.replace(".KS", "").replace(".KQ", "") if is_kr else s.ticker
            currency = "₩"if is_kr else "$"
            bp = f"{int(s.buy_price):,}" if is_kr else s.buy_price
            tp = f"{int(s.target_price):,}" if is_kr else s.target_price
            sp = f"{int(s.stop_price):,}" if is_kr else s.stop_price
            lines.append(
                f"{s.rank}. {ticker} {s.company_name} ({s.score}점)\n"
                f"   매수 {currency}{bp} / 목표 {currency}{tp} / 손절 {currency}{sp}"
            )

    if report.risk_warning:
        lines.append(f"\n⚠️ {report.risk_warning}")

    market_param = "kr" if is_kr else "us"
    lines.append(f"\n🔗 전체 리포트: {settings.frontend_url}?market={market_param}")
    lines.append("\n※ 본 리포트는 투자 참고용입니다. 투자 책임은 본인에게 있습니다.")
    return "\n".join(lines)


def _build_email_html(report: Report, stocks: list[Stock], market: str = "us") -> str:
    m = report.market_summary
    emoji = RISK_EMOJI.get(report.risk_level, "🟡")

    stock_rows = "".join(
        f"<tr><td>{s.rank}</td><td><b>{s.ticker}</b></td><td>{s.company_name}</td>"
        f"<td>{s.score}</td><td>${s.buy_price}</td><td>${s.target_price}</td><td>${s.stop_price}</td></tr>"
        for s in stocks
    )

    return f"""
<html><body style="font-family:sans-serif;max-width:600px;margin:auto">
<h2>📈 AI 투자 리포트 — {report.date}</h2>
<p style="font-size:18px">{emoji} <b>{report.risk_level}</b></p>
<h3>시장 현황</h3>
<ul>
  <li>Nasdaq: {_fmt_pct(m.get('nasdaq',0))}</li>
  <li>S&amp;P500: {_fmt_pct(m.get('sp500',0))}</li>
  <li>VIX: {m.get('vix',20):.1f}</li>
  <li>미국 10년 금리: {m.get('tnx',4.3):.2f}%</li>
</ul>
<h3>추천 종목 Top 5</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse;width:100%">
<tr><th>#</th><th>티커</th><th>기업명</th><th>점수</th><th>매수가</th><th>목표가</th><th>손절가</th></tr>
{stock_rows}
</table>
{"<p style='color:red'>⚠️ " + report.risk_warning + "</p>" if report.risk_warning else ""}
<p><a href="{settings.frontend_url}">전체 리포트 보기</a></p>
<hr><small>본 리포트는 투자 참고용입니다. 투자 결과에 대한 책임은 본인에게 있습니다.</small>
</body></html>
"""


async def _send_telegram(chat_id: str, text: str) -> None:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
        resp.raise_for_status()


async def _send_email(to_email: str, subject: str, html: str) -> None:
    url = "https://api.sendgrid.com/v3/mail/send"
    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": settings.sendgrid_from_email},
        "subject": subject,
        "content": [{"type": "text/html", "value": html}],
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {settings.sendgrid_api_key}"},
        )
        resp.raise_for_status()


def _fmt_pct(v: float) -> str:
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.2f}%"
