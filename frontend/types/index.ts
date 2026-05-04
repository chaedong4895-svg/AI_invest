export interface MarketSummary {
  nasdaq: number;
  sp500: number;
  dow: number;
  russell: number;
  vix: number;
  tnx: number;
}

export interface SectorItem {
  ticker: string;
  name: string;
  change_pct: number;
}

export interface SectorAnalysis {
  top3_bullish: SectorItem[];
  top3_bearish: SectorItem[];
  etf_changes: Record<string, number>;
}

export interface NewsItem {
  id: number;
  report_date: string;
  title: string;
  summary: string;
  sentiment: "positive" | "negative" | "neutral";
  sector: string | null;
  source: string | null;
  url: string | null;
  published_at: string | null;
  order_index: number;
}

export interface ScoreBreakdown {
  news: number;
  sector: number;
  price: number;
  volume: number;
  technical: number;
  volatility: number;
  event: number;
}

export interface Stock {
  id: number;
  report_date: string;
  rank: number;
  ticker: string;
  company_name: string;
  score: number;
  score_breakdown: ScoreBreakdown | null;
  reason: string;
  risk_factor: string;
  buy_price: number;
  target_price: number;
  stop_price: number;
}

export type RiskLevel = "Risk-On" | "Neutral" | "Risk-Off";

export interface Report {
  id: number;
  date: string;
  market: "us" | "kr";
  risk_level: RiskLevel;
  market_summary: MarketSummary;
  sector_analysis: SectorAnalysis | null;
  risk_warning: string | null;
  report_version: number;
  created_at: string;
  news_items: NewsItem[];
  stocks: Stock[];
}

export interface ReportSummary {
  date: string;
  market: "us" | "kr";
  risk_level: RiskLevel;
  market_summary: Record<string, number>;
  created_at: string;
}
