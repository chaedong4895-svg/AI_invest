"""시장 데이터 및 뉴스 수집 서비스 (US / KR 공용)"""
import logging
from datetime import datetime, timezone
from typing import Optional
import feedparser
import yfinance as yf
import pandas as pd

logger = logging.getLogger(__name__)

# ── 미국 ──────────────────────────────────────────────────────────────────────
INDEX_TICKERS = {
    "nasdaq": "^IXIC",
    "sp500": "^GSPC",
    "dow": "^DJI",
    "russell": "^RUT",
    "vix": "^VIX",
    "tnx": "^TNX",
}

SECTOR_ETFS = {
    "XLK": "기술",
    "XLF": "금융",
    "XLE": "에너지",
    "XLV": "헬스케어",
    "XLY": "소비재",
}

CANDIDATE_TICKERS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA",
    "AMD", "INTC", "AVGO", "ORCL", "CRM", "ADBE", "NFLX",
    "JPM", "BAC", "GS", "MS", "WFC",
    "JNJ", "UNH", "PFE", "ABBV", "MRK",
    "XOM", "CVX", "COP",
    "AMGN", "GILD", "REGN",
]

RSS_FEEDS = [
    {"source": "Reuters", "url": "https://feeds.reuters.com/reuters/businessNews"},
    {"source": "CNBC", "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html"},
    {"source": "MarketWatch", "url": "https://feeds.marketwatch.com/marketwatch/topstories"},
]

# ── 한국 ──────────────────────────────────────────────────────────────────────
KR_INDEX_TICKERS = {
    "kospi": "^KS11",
    "kosdaq": "^KQ11",
    "usd_krw": "KRW=X",   # 원달러 환율
}

# 섹터별 대표 종목 (섹터 강도 계산용)
KR_SECTOR_GROUPS = {
    "반도체":    ["005930.KS", "000660.KS", "009150.KS"],
    "IT/플랫폼": ["035420.KS", "035720.KS", "036570.KS"],
    "바이오":    ["207940.KS", "068270.KS", "128940.KS"],
    "자동차":    ["005380.KS", "000270.KS", "012330.KS"],
    "금융":      ["105560.KS", "055550.KS", "086790.KS"],
    "2차전지":   ["051910.KS", "006400.KS", "247540.KS"],
    "방산":      ["012450.KS", "047810.KS", "064350.KS"],
}

KR_CANDIDATE_TICKERS = [
    # 반도체/전자
    "005930.KS",  # 삼성전자
    "000660.KS",  # SK하이닉스
    "009150.KS",  # 삼성전기
    "066570.KS",  # LG전자
    # IT/플랫폼
    "035420.KS",  # NAVER
    "035720.KS",  # 카카오
    "036570.KS",  # 엔씨소프트
    "259960.KS",  # 크래프톤
    # 바이오
    "207940.KS",  # 삼성바이오로직스
    "068270.KS",  # 셀트리온
    "128940.KS",  # 한미약품
    "326030.KS",  # SK바이오팜
    # 자동차
    "005380.KS",  # 현대차
    "000270.KS",  # 기아
    "012330.KS",  # 현대모비스
    # 금융
    "105560.KS",  # KB금융
    "055550.KS",  # 신한지주
    "086790.KS",  # 하나금융지주
    "032830.KS",  # 삼성생명
    # 2차전지/화학
    "051910.KS",  # LG화학
    "006400.KS",  # 삼성SDI
    "247540.KS",  # 에코프로비엠
    "096770.KS",  # SK이노베이션
    # 방산/항공
    "012450.KS",  # 한화에어로스페이스
    "047810.KS",  # 한국항공우주
    "064350.KS",  # 현대로템
    # 통신
    "017670.KS",  # SK텔레콤
    "030200.KS",  # KT
]

# 한국어 회사명 매핑
KR_COMPANY_NAMES = {
    "005930.KS": "삼성전자",
    "000660.KS": "SK하이닉스",
    "009150.KS": "삼성전기",
    "066570.KS": "LG전자",
    "035420.KS": "NAVER",
    "035720.KS": "카카오",
    "036570.KS": "엔씨소프트",
    "259960.KS": "크래프톤",
    "207940.KS": "삼성바이오로직스",
    "068270.KS": "셀트리온",
    "128940.KS": "한미약품",
    "326030.KS": "SK바이오팜",
    "005380.KS": "현대차",
    "000270.KS": "기아",
    "012330.KS": "현대모비스",
    "105560.KS": "KB금융",
    "055550.KS": "신한지주",
    "086790.KS": "하나금융지주",
    "032830.KS": "삼성생명",
    "051910.KS": "LG화학",
    "006400.KS": "삼성SDI",
    "247540.KS": "에코프로비엠",
    "096770.KS": "SK이노베이션",
    "012450.KS": "한화에어로스페이스",
    "047810.KS": "한국항공우주",
    "064350.KS": "현대로템",
    "017670.KS": "SK텔레콤",
    "030200.KS": "KT",
}

KR_RSS_FEEDS = [
    {"source": "연합뉴스", "url": "https://www.yna.co.kr/rss/economy.xml"},
    {"source": "한국경제", "url": "https://www.hankyung.com/feed/all-news"},
    {"source": "이데일리", "url": "https://rss.edaily.co.kr/edaily/news/rss/stock.xml"},
    {"source": "머니투데이", "url": "https://news.mt.co.kr/mtview/rss/index.html"},
]


# ── 공통 헬퍼 ─────────────────────────────────────────────────────────────────

def _pct_change(ticker: str) -> float:
    """야후 파이낸스에서 등락률(%) 반환"""
    try:
        hist = yf.Ticker(ticker).history(period="2d")
        if len(hist) >= 2:
            prev, last = float(hist["Close"].iloc[-2]), float(hist["Close"].iloc[-1])
            return round((last - prev) / prev * 100, 2)
    except Exception as e:
        logger.warning(f"pct_change failed {ticker}: {e}")
    return 0.0


def _last_price(ticker: str) -> float:
    try:
        hist = yf.Ticker(ticker).history(period="1d")
        if not hist.empty:
            return round(float(hist["Close"].iloc[-1]), 2)
    except Exception:
        pass
    return 0.0


# ── 미국 시장 데이터 ──────────────────────────────────────────────────────────

def fetch_market_data() -> dict:
    result = {}
    for key, ticker in INDEX_TICKERS.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist["Close"].iloc[-2]
                last_close = hist["Close"].iloc[-1]
                change_pct = ((last_close - prev_close) / prev_close) * 100
                result[key] = round(float(change_pct), 2)
                if key == "vix":
                    result["vix_value"] = round(float(last_close), 2)
                elif key == "tnx":
                    result["tnx_value"] = round(float(last_close), 3)
            else:
                result[key] = 0.0
        except Exception as e:
            logger.warning(f"Failed to fetch {ticker}: {e}")
            result[key] = 0.0

    if "vix_value" not in result:
        result["vix_value"] = 20.0
    if "tnx_value" not in result:
        result["tnx_value"] = 4.3
    return result


def fetch_sector_data() -> dict:
    sector_data = {}
    for etf_ticker, name in SECTOR_ETFS.items():
        try:
            hist = yf.Ticker(etf_ticker).history(period="2d")
            if len(hist) >= 2:
                prev, last = hist["Close"].iloc[-2], hist["Close"].iloc[-1]
                pct = ((last - prev) / prev) * 100
                sector_data[etf_ticker] = {"name": name, "change_pct": round(float(pct), 2)}
            else:
                sector_data[etf_ticker] = {"name": name, "change_pct": 0.0}
        except Exception as e:
            logger.warning(f"Failed to fetch sector {etf_ticker}: {e}")
            sector_data[etf_ticker] = {"name": name, "change_pct": 0.0}
    return sector_data


# ── 한국 시장 데이터 ──────────────────────────────────────────────────────────

def fetch_kr_market_data() -> dict:
    """KOSPI / KOSDAQ / 원달러 환율 수집"""
    result = {}
    for key, ticker in KR_INDEX_TICKERS.items():
        try:
            hist = yf.Ticker(ticker).history(period="2d")
            if len(hist) >= 2:
                prev, last = float(hist["Close"].iloc[-2]), float(hist["Close"].iloc[-1])
                result[key] = round((last - prev) / prev * 100, 2)
                if key == "usd_krw":
                    result["usd_krw_value"] = round(last, 1)
                elif key == "kospi":
                    result["kospi_value"] = round(last, 2)
                elif key == "kosdaq":
                    result["kosdaq_value"] = round(last, 2)
            else:
                result[key] = 0.0
        except Exception as e:
            logger.warning(f"KR index failed {ticker}: {e}")
            result[key] = 0.0

    # 미국 VIX도 참고용으로 포함
    result["vix_value"] = _last_price("^VIX") or 20.0
    result["vix"] = _pct_change("^VIX")
    return result


def fetch_kr_sector_data() -> dict:
    """섹터 대표 종목 평균 등락률로 섹터 강도 계산"""
    sector_data = {}
    for sector_name, tickers in KR_SECTOR_GROUPS.items():
        pcts = []
        for t in tickers:
            pct = _pct_change(t)
            if pct != 0.0:
                pcts.append(pct)
        avg = round(sum(pcts) / len(pcts), 2) if pcts else 0.0
        sector_data[sector_name] = {"name": sector_name, "change_pct": avg}
    return sector_data


# ── 공통: 섹터 분석 / 종목 데이터 ────────────────────────────────────────────

def build_sector_analysis(sector_data: dict) -> dict:
    items = [
        {"ticker": k, "name": v["name"], "change_pct": v["change_pct"]}
        for k, v in sector_data.items()
    ]
    sorted_items = sorted(items, key=lambda x: x["change_pct"], reverse=True)
    return {
        "top3_bullish": sorted_items[:3],
        "top3_bearish": sorted_items[-3:][::-1],
        "etf_changes": {k: v["change_pct"] for k, v in sector_data.items()},
    }


def fetch_stock_data(tickers: list[str], market: str = "us") -> dict:
    """종목 가격·거래량 데이터 수집 (US / KR 공용)"""
    stock_data = {}
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="30d")
            info = t.info

            if hist.empty:
                continue

            last = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) >= 2 else hist.iloc[-1]

            avg_volume = hist["Volume"].mean()
            volume_ratio = float(last["Volume"]) / avg_volume if avg_volume > 0 else 1.0

            closes = hist["Close"].values
            ma5 = closes[-5:].mean() if len(closes) >= 5 else closes[-1]
            ma20 = closes[-20:].mean() if len(closes) >= 20 else closes[-1]
            rsi = _calc_rsi(hist["Close"])

            # 한국 종목은 한국어 이름 우선
            if market == "kr":
                company_name = KR_COMPANY_NAMES.get(ticker, info.get("longName", ticker))
            else:
                company_name = info.get("longName", ticker)

            atr = _calc_atr(hist)
            stock_data[ticker] = {
                "company_name": company_name,
                "last_price": round(float(last["Close"]), 0 if market == "kr" else 2),
                "prev_close": round(float(prev["Close"]), 0 if market == "kr" else 2),
                "volume": int(last["Volume"]),
                "avg_volume": round(float(avg_volume)),
                "volume_ratio": round(volume_ratio, 2),
                "ma5": round(float(ma5), 0 if market == "kr" else 2),
                "ma20": round(float(ma20), 0 if market == "kr" else 2),
                "rsi": round(rsi, 1),
                "beta": info.get("beta", 1.0) or 1.0,
                "earnings_date": _get_earnings_date(info),
                "atr": round(atr, 0 if market == "kr" else 2),
            }
        except Exception as e:
            logger.warning(f"Failed to fetch stock {ticker}: {e}")
    return stock_data


def _calc_rsi(closes: pd.Series, period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    delta = closes.diff().dropna()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    return float(val) if not pd.isna(val) else 50.0


def _calc_atr(hist: pd.DataFrame, period: int = 14) -> float:
    """Average True Range — 손절 폭 결정용"""
    if len(hist) < 2:
        return 0.0
    high = hist["High"]
    low  = hist["Low"]
    prev_close = hist["Close"].shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low  - prev_close).abs(),
    ], axis=1).max(axis=1)
    atr = tr.rolling(period).mean().iloc[-1]
    return float(atr) if not pd.isna(atr) else 0.0


def _get_earnings_date(info: dict) -> Optional[str]:
    ts = info.get("earningsTimestamp") or info.get("earningsDate")
    if not ts:
        return None
    if isinstance(ts, list):
        ts = ts[0]
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except Exception:
        return None


def fetch_news(max_items: int = 30, market: str = "us") -> list[dict]:
    """RSS 피드에서 뉴스 수집"""
    feeds = KR_RSS_FEEDS if market == "kr" else RSS_FEEDS
    articles = []
    for feed_cfg in feeds:
        try:
            feed = feedparser.parse(feed_cfg["url"])
            for entry in feed.entries[:10]:
                articles.append({
                    "source": feed_cfg["source"],
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", entry.get("description", "")),
                    "url": entry.get("link", ""),
                    "published_at": _parse_published(entry),
                })
        except Exception as e:
            logger.warning(f"Failed to fetch RSS {feed_cfg['source']}: {e}")

    seen = set()
    unique = []
    for a in articles:
        if a["title"] not in seen:
            seen.add(a["title"])
            unique.append(a)

    unique.sort(key=lambda x: x["published_at"] or datetime.min, reverse=True)
    return unique[:max_items]


def _parse_published(entry) -> Optional[datetime]:
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            import time
            return datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        except Exception:
            pass
    return None
