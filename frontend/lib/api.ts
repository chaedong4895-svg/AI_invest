import type { Report, ReportSummary, NewsItem, Stock } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { next: { revalidate: 300 } });
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  getLatestReport: (market: "us" | "kr" = "us") =>
    fetchJSON<Report>(`/api/v1/reports/latest?market=${market}`),

  getReport: (date: string, market: "us" | "kr" = "us") =>
    fetchJSON<Report>(`/api/v1/reports/${date}?market=${market}`),

  listReports: (page = 1, limit = 20, market: "us" | "kr" = "us") =>
    fetchJSON<ReportSummary[]>(`/api/v1/reports?page=${page}&limit=${limit}&market=${market}`),

  getNews: (date: string, market: "us" | "kr" = "us") =>
    fetchJSON<NewsItem[]>(`/api/v1/news/${date}?market=${market}`),

  getStocks: (date: string, market: "us" | "kr" = "us") =>
    fetchJSON<Stock[]>(`/api/v1/stocks/${date}?market=${market}`),

  getStock: (date: string, ticker: string, market: "us" | "kr" = "us") =>
    fetchJSON<Stock>(`/api/v1/stocks/${date}/${ticker}?market=${market}`),

  subscribe: (type: string, contact: string) =>
    fetch(`${BASE}/api/v1/subscribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type, contact }),
    }).then((r) => r.json()),

  unsubscribe: (contact: string) =>
    fetch(`${BASE}/api/v1/subscribe?contact=${encodeURIComponent(contact)}`, {
      method: "DELETE",
    }).then((r) => r.json()),
};
