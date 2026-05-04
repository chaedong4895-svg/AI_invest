# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI 투자 리포트 시스템** — 미국 증시 마감 후 데이터를 자동 수집·분석하여 매일 오전 7시 AI 기반 투자 리포트를 생성·발송하는 정보 플랫폼. 자동매매 없음. 투자 정보 제공 서비스.

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Backend | FastAPI (Python) + SQLAlchemy 2 + PostgreSQL |
| AI | OpenAI API (GPT-4o for rationale, GPT-4o-mini for news) |
| Scheduler | APScheduler (inside FastAPI process) |
| Notifications | Telegram Bot API + SendGrid |
| Infra | Docker Compose (local), Vercel (FE), Railway (BE) |

## Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload        # dev server at :8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # dev server at :3000
npm run build
npm run lint
```

### Docker (all services)
```bash
cp .env.example .env   # fill in API keys
docker-compose up      # postgres + redis + backend + frontend
```

## Architecture

### Automated Pipeline (runs daily KST 06:05)
```
APScheduler → data_collector → news_processor (OpenAI) → scorer → report_generator → PostgreSQL
                                                                                      ↓
                                                                 KST 07:00 → notifier → Telegram / SendGrid
```

### Key Services (`backend/services/`)
- **`data_collector.py`** — Yahoo Finance (yfinance) for 6 indices + 5 sector ETFs + 30 candidate stocks; RSS feeds (Reuters, CNBC, MarketWatch)
- **`news_processor.py`** — OpenAI batch calls: 2-sentence Korean summary + sentiment (positive/negative/neutral) + sector tag (XLK/XLF/XLE/XLV/XLY)
- **`scorer.py`** — 7-item weighted scoring (100pt max): News 25, Sector 20, Price 15, Volume 15, Technical 10, Volatility 10, Event 5. `determine_risk_level()` → Risk-On/Neutral/Risk-Off
- **`report_generator.py`** — Full pipeline coordinator: runs steps 1–9, writes to DB atomically

### Database Tables
- `reports` — one row per date (risk_level, market_summary JSONB, sector_analysis JSONB)
- `news` — 5–10 rows per date, FK → reports.date
- `stocks` — 5 rows per date (rank 1–5), FK → reports.date
- `subscribers` — telegram/email contacts
- `notification_logs` — delivery audit trail

### Frontend Pages (Next.js App Router)
- `/` — Dashboard (latest report, ISR 5min)
- `/report/[date]` — Historical report detail
- `/archive` — Calendar-style report list
- `/stock/[ticker]?date=` — Stock detail with radar chart (client component)
- `/subscribe` — Telegram/email signup
- `/admin` — Manual trigger for generate/notify (requires `x-admin-key` header)

## Environment Variables

Copy `.env.example` → `.env`. Required keys:
- `OPENAI_API_KEY` — GPT-4o access
- `TELEGRAM_BOT_TOKEN` / `TELEGRAM_ADMIN_CHAT_ID` — notification bot
- `SENDGRID_API_KEY` / `SENDGRID_FROM_EMAIL` — email delivery
- `ADMIN_SECRET_KEY` — protects `/api/v1/admin/*` endpoints

## Key Design Decisions
- Risk Level判定: Nasdaq % + VIX threshold (Risk-Off if Nasdaq < -1% OR VIX > 25)
- Stock prices: buy = last close, target = buy × 1.10, stop = buy × 0.95
- OpenAI cost control: news uses `gpt-4o-mini`; rationale uses `gpt-4o`; only top-15 news articles sent
- Scheduler time: `collect_and_generate` at UTC 21:05 (KST 06:05), `send_notifications` at UTC 22:00 (KST 07:00)
- Error fallback: data collection failures retry 3×; OpenAI failures use raw title as summary
