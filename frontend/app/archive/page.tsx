import { api } from "@/lib/api";
import MarketTabs from "@/components/MarketTabs";
import type { RiskLevel } from "@/types";
import clsx from "clsx";

export const revalidate = 300;

const RISK_STYLE: Record<RiskLevel, string> = {
  "Risk-On": "bg-green-100 text-green-700",
  Neutral: "bg-yellow-100 text-yellow-700",
  "Risk-Off": "bg-red-100 text-red-700",
};
const RISK_EMOJI: Record<RiskLevel, string> = {
  "Risk-On": "🟢",
  Neutral: "🟡",
  "Risk-Off": "🔴",
};

export default async function ArchivePage({
  searchParams,
}: {
  searchParams: { market?: string };
}) {
  const market = searchParams.market === "kr" ? "kr" : "us";
  const reports = await api.listReports(1, 60, market).catch(() => []);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-slate-900">리포트 아카이브</h1>
        <MarketTabs active={market} basePath="/archive" />
      </div>

      {reports.length === 0 ? (
        <div className="text-center py-12 text-slate-400">
          {market === "kr" ? "한국" : "미국"} 리포트가 없습니다.
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((r) => {
            const m = r.market_summary as Record<string, number>;
            const isKr = r.market === "kr";
            const cards = isKr
              ? [
                  { label: "KOSPI", v: m.kospi ?? 0 },
                  { label: "KOSDAQ", v: m.kosdaq ?? 0 },
                  { label: "VIX", v: m.vix ?? 20, abs: true },
                ]
              : [
                  { label: "Nasdaq", v: m.nasdaq ?? 0 },
                  { label: "S&P500", v: m.sp500 ?? 0 },
                  { label: "VIX", v: m.vix ?? 20, abs: true },
                ];

            return (
              <a
                key={`${r.date}-${r.market}`}
                href={`/report/${r.date}?market=${r.market}`}
                className="bg-white border border-slate-200 rounded-xl p-4 hover:border-blue-300 hover:shadow-sm transition"
              >
                <div className="flex items-center justify-between mb-3">
                  <span className="text-slate-500 text-sm">{r.date}</span>
                  <span
                    className={clsx(
                      "text-xs px-2 py-0.5 rounded-full font-medium",
                      RISK_STYLE[r.risk_level as RiskLevel]
                    )}
                  >
                    {RISK_EMOJI[r.risk_level as RiskLevel]} {r.risk_level}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs text-center">
                  {cards.map(({ label, v, abs }) => (
                    <div key={label} className="bg-slate-50 rounded-lg p-2">
                      <div className="text-slate-400">{label}</div>
                      <div
                        className={clsx(
                          "font-bold",
                          abs ? "text-slate-700" : v >= 0 ? "text-green-600" : "text-red-500"
                        )}
                      >
                        {abs ? v.toFixed(1) : `${v >= 0 ? "+" : ""}${v.toFixed(2)}%`}
                      </div>
                    </div>
                  ))}
                </div>
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}
