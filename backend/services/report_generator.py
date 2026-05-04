"""리포트 생성 파이프라인 (US / KR 공용)"""
import logging
from datetime import date
from openai import OpenAI
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models import Report, NewsItem, Stock
from .data_collector import (
    fetch_market_data, fetch_sector_data,
    fetch_kr_market_data, fetch_kr_sector_data,
    build_sector_analysis, fetch_stock_data, fetch_news,
    CANDIDATE_TICKERS, KR_CANDIDATE_TICKERS,
)
from .news_processor import process_news_batch, generate_stock_rationale
from .scorer import score_stock, determine_risk_level, calc_prices

logger = logging.getLogger(__name__)
settings = get_settings()


def run_pipeline(db: Session, report_date: date = None, market: str = "us") -> Report:
    """전체 리포트 생성 파이프라인"""
    if report_date is None:
        report_date = date.today()

    logger.info(f"[Pipeline] Starting — market={market}, date={report_date}")

    # 1. 시장 데이터 수집
    logger.info("[Pipeline] Step 1: Market data")
    if market == "kr":
        market_data = fetch_kr_market_data()
        sector_data = fetch_kr_sector_data()
        candidate_tickers = KR_CANDIDATE_TICKERS
    else:
        market_data = fetch_market_data()
        sector_data = fetch_sector_data()
        candidate_tickers = CANDIDATE_TICKERS

    sector_analysis = build_sector_analysis(sector_data)
    risk_level = determine_risk_level(market_data, market)
    logger.info(f"[Pipeline] Risk level: {risk_level}")

    # 2. 뉴스 수집 + AI 처리
    logger.info("[Pipeline] Step 2: News")
    raw_news = fetch_news(max_items=25, market=market)
    processed_news = process_news_batch(raw_news[:15])

    # 3. 종목 수집 + 점수화
    logger.info("[Pipeline] Step 3: Stock scoring")
    stock_data = fetch_stock_data(candidate_tickers, market=market)

    scored = []
    for ticker, data in stock_data.items():
        try:
            result = score_stock(ticker, data, processed_news, sector_data, market)
            scored.append({
                "ticker": ticker,
                "company_name": data.get("company_name", ticker),
                "score": result["total"],
                "score_breakdown": result["breakdown"],
                "last_price": data.get("last_price", 0),
                "raw_data": {k: v for k, v in data.items() if k != "company_name"},
            })
        except Exception as e:
            logger.warning(f"Scoring failed {ticker}: {e}")

    top5 = sorted(scored, key=lambda x: x["score"], reverse=True)[:5]

    # 4. AI 추천 사유
    logger.info("[Pipeline] Step 4: AI rationale")
    client = OpenAI(api_key=settings.openai_api_key)
    for stock in top5:
        rationale = generate_stock_rationale(
            client,
            stock["ticker"],
            stock["company_name"],
            stock["score"],
            stock["score_breakdown"],
            risk_level,
        )
        stock.update(rationale)

    # 5. 리스크 경고
    risk_warning = _build_risk_warning(market_data, risk_level, market)

    # 6. DB 저장
    logger.info("[Pipeline] Step 5: Saving")
    existing = db.query(Report).filter(
        Report.date == report_date,
        Report.market == market,
    ).first()

    if existing:
        version = existing.report_version + 1  # capture before flush (DetachedInstanceError 방지)
        db.delete(existing)
        # FK cascade 없으므로 연관 행 직접 삭제
        db.query(NewsItem).filter(NewsItem.report_date == report_date, NewsItem.report_market == market).delete()
        db.query(Stock).filter(Stock.report_date == report_date, Stock.report_market == market).delete()
        db.flush()
    else:
        version = 1

    report = Report(
        date=report_date,
        market=market,
        risk_level=risk_level,
        market_summary=_build_market_summary(market_data, market),
        sector_analysis=sector_analysis,
        risk_warning=risk_warning,
        report_version=version,
    )
    db.add(report)
    db.flush()

    for item in processed_news[:10]:
        db.add(NewsItem(
            report_date=report_date,
            report_market=market,
            title=item.get("title", ""),
            summary=item.get("summary", ""),
            sentiment=item.get("sentiment", "neutral"),
            sector=item.get("sector"),
            source=item.get("source"),
            url=item.get("url"),
            published_at=item.get("published_at"),
            order_index=item.get("order_index", 1),
        ))

    for rank, stock in enumerate(top5, start=1):
        raw = stock.get("raw_data", {})
        prices = calc_prices(
            stock["last_price"], market,
            atr=raw.get("atr", 0.0),
            beta=raw.get("beta", 1.0),
        )
        db.add(Stock(
            report_date=report_date,
            report_market=market,
            rank=rank,
            ticker=stock["ticker"],
            company_name=stock["company_name"],
            score=stock["score"],
            score_breakdown=stock["score_breakdown"],
            reason=stock.get("reason", ""),
            risk_factor=stock.get("risk_factor", ""),
            buy_price=prices["buy_price"],
            target_price=prices["target_price"],
            stop_price=prices["stop_price"],
            raw_data=stock.get("raw_data"),
        ))

    db.commit()
    db.refresh(report)
    logger.info(f"[Pipeline] Done — ID={report.id}, market={market}, date={report_date}")
    return report


def _build_market_summary(market_data: dict, market: str) -> dict:
    if market == "kr":
        return {
            "kospi":         market_data.get("kospi", 0),
            "kosdaq":        market_data.get("kosdaq", 0),
            "kospi_value":   market_data.get("kospi_value", 0),
            "kosdaq_value":  market_data.get("kosdaq_value", 0),
            "usd_krw":       market_data.get("usd_krw", 0),
            "usd_krw_value": market_data.get("usd_krw_value", 1300),
            "vix":           market_data.get("vix_value", 20),
        }
    return {
        "nasdaq":  market_data.get("nasdaq", 0),
        "sp500":   market_data.get("sp500", 0),
        "dow":     market_data.get("dow", 0),
        "russell": market_data.get("russell", 0),
        "vix":     market_data.get("vix_value", 20),
        "tnx":     market_data.get("tnx_value", 4.3),
    }


def _build_risk_warning(market_data: dict, risk_level: str, market: str) -> str | None:
    warnings = []
    vix = market_data.get("vix_value", 20)
    if vix > 30:
        warnings.append(f"VIX {vix:.1f} — 극도의 공포 구간입니다. 신규 진입 자제를 권고합니다.")
    elif vix > 25:
        warnings.append(f"VIX {vix:.1f} — 시장 변동성이 높습니다.")

    if market == "kr":
        usd_krw = market_data.get("usd_krw", 0)
        if usd_krw > 2.0:
            val = market_data.get("usd_krw_value", 1300)
            warnings.append(f"원달러 환율 급등({val:.0f}원) — 외국인 수급 이탈 주의.")
    else:
        tnx_chg = market_data.get("tnx", 0)
        if tnx_chg > 3.0:
            tnx = market_data.get("tnx_value", 4.3)
            warnings.append(f"미국 10년 금리 급등({tnx:.2f}%) — 성장주에 부담.")

    if risk_level == "Risk-Off":
        warnings.append("현금 비중 확대 및 리스크 축소를 고려하세요.")

    return " ".join(warnings) if warnings else None
