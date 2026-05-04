"""OpenAI를 활용한 뉴스 요약 및 감성 분류"""
import json
import logging
from openai import OpenAI
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def process_news_batch(articles: list[dict]) -> list[dict]:
    """뉴스 배치 처리: 요약 + 감성 + 섹터 매핑"""
    client = OpenAI(api_key=settings.openai_api_key)
    results = []

    for i, article in enumerate(articles):
        try:
            processed = _process_single_news(client, article)
            processed["order_index"] = i + 1
            results.append(processed)
        except Exception as e:
            logger.warning(f"Failed to process news [{article['title'][:50]}]: {e}")
            results.append({
                **article,
                "summary": article["title"],
                "sentiment": "neutral",
                "sector": None,
                "order_index": i + 1,
            })

    return results


def _process_single_news(client: OpenAI, article: dict) -> dict:
    prompt = f"""다음 뉴스를 분석해주세요.

뉴스 제목: {article['title']}
내용: {article['content'][:500] if article.get('content') else ''}

JSON 형식으로만 응답하세요:
{{"summary": "한국어 2문장 요약", "sentiment": "positive|negative|neutral", "sector": "XLK|XLF|XLE|XLV|XLY|null"}}"""

    response = client.chat.completions.create(
        model=settings.openai_model_news,
        messages=[
            {
                "role": "system",
                "content": "You are a financial news analyst. Respond only with valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=200,
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    data = json.loads(response.choices[0].message.content)
    return {
        **article,
        "summary": data.get("summary", article["title"]),
        "sentiment": data.get("sentiment", "neutral"),
        "sector": data.get("sector") if data.get("sector") != "null" else None,
    }


def generate_stock_rationale(
    client: OpenAI,
    ticker: str,
    company: str,
    score: int,
    score_breakdown: dict,
    risk_level: str,
) -> dict:
    """종목 추천 사유 및 리스크 문장 생성"""
    prompt = f"""다음 종목에 대한 투자 추천 사유와 리스크를 한국어로 작성해주세요.

종목: {ticker} ({company})
점수: {score}/100
점수 근거: {json.dumps(score_breakdown, ensure_ascii=False)}
시장 상태: {risk_level}

JSON 형식으로만 응답하세요:
{{"reason": "2~3문장 추천 사유", "risk_factor": "1~2문장 리스크"}}"""

    try:
        response = client.chat.completions.create(
            model=settings.openai_model_report,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional stock analyst. Respond only with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.5,
            response_format={"type": "json_object"},
        )
        data = json.loads(response.choices[0].message.content)
        return {
            "reason": data.get("reason", "데이터 기반 추천 종목입니다."),
            "risk_factor": data.get("risk_factor", "시장 변동성에 주의하세요."),
        }
    except Exception as e:
        logger.warning(f"Failed to generate rationale for {ticker}: {e}")
        return {
            "reason": f"{company}는 현재 강한 모멘텀을 보이고 있습니다.",
            "risk_factor": "시장 전반의 변동성에 주의가 필요합니다.",
        }
