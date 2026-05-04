import { api } from "@/lib/api";
import RiskBadge from "@/components/RiskBadge";
import MarketTabs from "@/components/MarketTabs";
import MarketSummary from "@/components/MarketSummary";
import NewsCard from "@/components/NewsCard";
import StockCard from "@/components/StockCard";
import SectorBar from "@/components/SectorBar";
import type { RiskLevel } from "@/types";
import { notFound } from "next/navigation";

export const revalidate = 3600;

export default async function ReportPage({
  params,
  searchParams,
}: {
  params: { date: string };
  searchParams: { market?: string };
}) {
  const market = searchParams.market === "kr" ? "kr" : "us";

  let report;
  try {
    report = await api.getReport(params.date, market);
  } catch {
    notFound();
  }

  const sector = report.sector_analysis;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <a
            href={`/archive?market=${market}`}
            className="text-sm text-blue-600 hover:underline"
          >
            ← 아카이브
          </a>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-slate-900">{report.date} 리포트</h1>
            <MarketTabs active={market} basePath={`/report/${params.date}`} />
          </div>
        </div>
        <RiskBadge level={report.risk_level as RiskLevel} />
      </div>

      {report.risk_warning && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl px-4 py-3 text-sm flex gap-2">
          <span>⚠️</span>
          <span>{report.risk_warning}</span>
        </div>
      )}

      <MarketSummary summary={report.market_summary as any} market={market} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-lg font-semibold text-slate-800">핵심 뉴스</h2>
          {report.news_items.map((item) => (
            <NewsCard key={item.id} item={item} />
          ))}
        </div>
        <div>
          {sector && (
            <SectorBar bullish={sector.top3_bullish} bearish={sector.top3_bearish} />
          )}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-slate-800 mb-3">추천 종목 Top 5</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
          {report.stocks.map((stock) => (
            <StockCard key={stock.id} stock={stock} />
          ))}
        </div>
      </div>
    </div>
  );
}
