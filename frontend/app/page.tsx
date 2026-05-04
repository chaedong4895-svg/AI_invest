import { api } from "@/lib/api";
import RiskBadge from "@/components/RiskBadge";
import MarketTabs from "@/components/MarketTabs";
import MarketSummary from "@/components/MarketSummary";
import NewsCard from "@/components/NewsCard";
import StockCard from "@/components/StockCard";
import SectorBar from "@/components/SectorBar";
import type { RiskLevel } from "@/types";

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: { market?: string };
}) {
  const market = searchParams.market === "kr" ? "kr" : "us";

  let report;
  try {
    report = await api.getLatestReport(market);
  } catch {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="font-semibold">오늘의 리포트</h1>
          <MarketTabs active={market} />
        </div>
        <p className="text-slate-400 text-sm py-12 text-center">
          리포트가 아직 준비 중입니다. 매일 오전 7시에 업데이트됩니다.
        </p>
      </div>
    );
  }

  const sector = report.sector_analysis;

  return (
    <div className="space-y-8">

      {/* 헤더: 날짜 + 탭 + 리스크 */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <h1 className="font-semibold text-slate-900">{report.date}</h1>
            <MarketTabs active={market} />
          </div>
          <RiskBadge level={report.risk_level as RiskLevel} />
        </div>
      </div>

      {/* 리스크 경고 */}
      {report.risk_warning && (
        <p className="text-sm text-red-600 bg-red-50 rounded-lg px-4 py-2">
          ⚠ {report.risk_warning}
        </p>
      )}

      {/* 시장 지수 */}
      <MarketSummary summary={report.market_summary as any} market={market} />

      {/* 추천 종목 + 섹터 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-3">추천 종목</div>
          {report.stocks.map((stock) => (
            <StockCard key={stock.id} stock={stock} />
          ))}
        </div>
        <div>
          {sector && (
            <SectorBar bullish={sector.top3_bullish} bearish={sector.top3_bearish} />
          )}
        </div>
      </div>

      {/* 뉴스 */}
      <div>
        <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-1">뉴스</div>
        {report.news_items.slice(0, 7).map((item) => (
          <NewsCard key={item.id} item={item} />
        ))}
      </div>

    </div>
  );
}
