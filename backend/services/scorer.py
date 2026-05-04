"""종목 점수화 로직 (7개 항목 가중 합산, 100점 만점)"""
from datetime import date, datetime, timezone


# ── 미국 섹터 매핑 ─────────────────────────────────────────────────────────────
SECTOR_TICKER_MAP = {
    "XLK": ["AAPL", "MSFT", "NVDA", "AMD", "INTC", "AVGO", "ORCL", "CRM", "ADBE"],
    "XLF": ["JPM", "BAC", "GS", "MS", "WFC"],
    "XLE": ["XOM", "CVX", "COP"],
    "XLV": ["JNJ", "UNH", "PFE", "ABBV", "MRK", "AMGN", "GILD", "REGN"],
    "XLY": ["AMZN", "TSLA", "NFLX"],
}

# ── 한국 섹터 매핑 ─────────────────────────────────────────────────────────────
KR_SECTOR_TICKER_MAP = {
    "반도체":    ["005930.KS", "000660.KS", "009150.KS"],
    "IT/플랫폼": ["035420.KS", "035720.KS", "036570.KS", "259960.KS"],
    "바이오":    ["207940.KS", "068270.KS", "128940.KS", "326030.KS"],
    "자동차":    ["005380.KS", "000270.KS", "012330.KS"],
    "금융":      ["105560.KS", "055550.KS", "086790.KS", "032830.KS"],
    "2차전지":   ["051910.KS", "006400.KS", "247540.KS", "096770.KS"],
    "방산":      ["012450.KS", "047810.KS", "064350.KS"],
    "통신":      ["017670.KS", "030200.KS"],
}


def score_stock(
    ticker: str,
    stock_data: dict,
    news_items: list[dict],
    sector_data: dict,
    market: str = "us",
) -> dict:
    """종목 점수 계산 — 항목별 점수 반환"""
    sector_map = KR_SECTOR_TICKER_MAP if market == "kr" else SECTOR_TICKER_MAP
    breakdown = {
        "news":       _score_news(ticker, news_items, market),
        "sector":     _score_sector(ticker, sector_data, sector_map),
        "price":      _score_price(stock_data),
        "volume":     _score_volume(stock_data),
        "technical":  _score_technical(stock_data),
        "volatility": _score_volatility(stock_data),
        "event":      _score_event(stock_data),
    }
    total = sum(breakdown.values())
    return {"total": min(total, 100), "breakdown": breakdown}


# ── 개별 점수 함수 ─────────────────────────────────────────────────────────────

def _score_news(ticker: str, news_items: list[dict], market: str = "us") -> int:
    """뉴스 영향 (25점)"""
    sentiment_map = {"positive": 1, "neutral": 0, "negative": -1}
    score = 0
    matched = 0

    from .data_collector import KR_COMPANY_NAMES
    search_keys = set()
    search_keys.add(ticker.upper().replace(".KS", "").replace(".KQ", ""))
    if market == "kr" and ticker in KR_COMPANY_NAMES:
        search_keys.add(KR_COMPANY_NAMES[ticker])

    for item in news_items:
        text = ((item.get("title") or "") + " " + (item.get("summary") or "")).upper()
        if any(k.upper() in text for k in search_keys):
            s = sentiment_map.get(item.get("sentiment", "neutral"), 0)
            score += 5 * s
            matched += 1

    if matched == 0:
        return 8  # 뉴스 미언급 — 중립 기본값보다 낮게 설정
    return max(0, min(25, 12 + score))


def _score_sector(ticker: str, sector_data: dict, sector_map: dict) -> int:
    """섹터 강도 (20점)"""
    for sector_key, tickers in sector_map.items():
        if ticker in tickers:
            pct = sector_data.get(sector_key, {}).get("change_pct", 0.0)
            normalized = (pct + 3) / 6   # -3~+3% → 0~1
            return max(0, min(20, int(normalized * 20)))
    return 10


def _score_price(stock_data: dict) -> int:
    """가격 흐름 (15점)"""
    last = stock_data.get("last_price", 0)
    ma5  = stock_data.get("ma5", last)
    ma20 = stock_data.get("ma20", last)
    if last > ma5 > ma20:
        return 15
    elif last > ma20:
        return 10
    elif last > ma5:
        return 8
    else:
        return 4


def _score_volume(stock_data: dict) -> int:
    """거래량 (15점)"""
    ratio = stock_data.get("volume_ratio", 1.0)
    if ratio >= 2.0:   return 15
    elif ratio >= 1.5: return 12
    elif ratio >= 1.0: return 8
    else:              return 4


def _score_technical(stock_data: dict) -> int:
    """기술적 위치 (10점) — RSI"""
    rsi = stock_data.get("rsi", 50)
    if 40 <= rsi <= 60:          return 10
    elif 30 <= rsi < 40 or 60 < rsi <= 70: return 7
    elif rsi < 30:               return 5
    else:                        return 3


def _score_volatility(stock_data: dict) -> int:
    """변동성 (10점) — 베타 (낮을수록 고점수)"""
    beta = float(stock_data.get("beta", 1.0) or 1.0)
    if beta <= 0.8:   return 10
    elif beta <= 1.0: return 8
    elif beta <= 1.3: return 6
    elif beta <= 1.6: return 4
    else:             return 2


def _score_event(stock_data: dict) -> int:
    """이벤트 리스크 (5점)"""
    earnings_date = stock_data.get("earnings_date")
    if not earnings_date:
        return 5
    try:
        ed = datetime.strptime(earnings_date, "%Y-%m-%d").date()
        days = (ed - date.today()).days
        if days < 0 or days > 30: return 5
        elif days <= 3:  return 1
        elif days <= 7:  return 2
        elif days <= 14: return 3
        else:            return 4
    except Exception:
        return 5


def determine_risk_level(market_data: dict, market: str = "us") -> str:
    """시장 상태 판정"""
    if market == "kr":
        kospi_pct = market_data.get("kospi", 0)
        vix = market_data.get("vix_value", 20)
        if kospi_pct < -1.0 or vix > 25:
            return "Risk-Off"
        elif kospi_pct >= 0 and vix < 20:
            return "Risk-On"
        else:
            return "Neutral"
    else:
        nasdaq_pct = market_data.get("nasdaq", 0)
        vix = market_data.get("vix_value", 20)
        if nasdaq_pct < -1.0 or vix > 25:
            return "Risk-Off"
        elif nasdaq_pct >= 0 and vix < 20:
            return "Risk-On"
        else:
            return "Neutral"


def calc_prices(last_price: float, market: str = "us", atr: float = 0.0, beta: float = 1.0) -> dict:
    """매수가 / 목표가 / 손절가 (ATR 기반 동적 손절)"""
    decimals = 0 if market == "kr" else 2
    buy    = round(last_price, decimals)
    target = round(buy * 1.10, decimals)

    if atr > 0:
        # ATR × 2배, 단 최소 3% / 최대 10% 범위로 clamp
        raw_stop = buy - 2.0 * atr
        min_stop = buy * 0.90
        max_stop = buy * 0.97
        stop = round(max(min_stop, min(max_stop, raw_stop)), decimals)
    else:
        # ATR 없으면 베타 반영 고정 비율 (베타 높을수록 더 넓은 손절)
        ratio = max(0.90, 0.97 - 0.02 * (float(beta) - 1.0))
        stop = round(buy * ratio, decimals)

    return {"buy_price": buy, "target_price": target, "stop_price": stop}
