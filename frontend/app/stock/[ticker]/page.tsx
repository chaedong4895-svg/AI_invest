"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import type { Stock } from "@/types";
import { api } from "@/lib/api";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
} from "recharts";

const BREAKDOWN_LABELS: Record<string, string> = {
  news: "뉴스 영향",
  sector: "섹터 강도",
  price: "가격 흐름",
  volume: "거래량",
  technical: "기술적 위치",
  volatility: "변동성",
  event: "이벤트 리스크",
};

export default function StockDetailPage({ params }: { params: { ticker: string } }) {
  const searchParams = useSearchParams();
  const reportDate = searchParams.get("date") ?? "";
  const [stock, setStock] = useState<Stock | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!reportDate) { setError(true); return; }
    api.getStock(reportDate, params.ticker)
      .then(setStock)
      .catch(() => setError(true));
  }, [params.ticker, reportDate]);

  if (error) {
    return <div className="text-center py-20 text-slate-400">종목 정보를 찾을 수 없습니다.</div>;
  }
  if (!stock) {
    return <div className="text-center py-20 text-slate-400">불러오는 중...</div>;
  }

  const radarData = Object.entries(stock.score_breakdown ?? {}).map(([key, val]) => ({
    subject: BREAKDOWN_LABELS[key] ?? key,
    value: val as number,
    max: key === "news" || key === "sector" ? (key === "news" ? 25 : 20) : key === "price" || key === "volume" ? 15 : key === "technical" || key === "volatility" ? 10 : 5,
  }));

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <a href={`/report/${stock.report_date}`} className="text-sm text-blue-600 hover:underline">
        ← {stock.report_date} 리포트
      </a>

      <div className="bg-white border border-slate-200 rounded-2xl p-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-3xl font-bold text-slate-900">{stock.ticker}</div>
            <div className="text-slate-500">{stock.company_name}</div>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-blue-600">{stock.score}</div>
            <div className="text-sm text-slate-400">/ 100점</div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3 mt-6">
          <div className="bg-blue-50 rounded-xl p-3 text-center">
            <div className="text-xs text-blue-500 font-medium">매수가</div>
            <div className="text-lg font-bold text-slate-800">${stock.buy_price}</div>
          </div>
          <div className="bg-green-50 rounded-xl p-3 text-center">
            <div className="text-xs text-green-600 font-medium">목표가 (+10%)</div>
            <div className="text-lg font-bold text-slate-800">${stock.target_price}</div>
          </div>
          <div className="bg-red-50 rounded-xl p-3 text-center">
            <div className="text-xs text-red-500 font-medium">손절가 (-5%)</div>
            <div className="text-lg font-bold text-slate-800">${stock.stop_price}</div>
          </div>
        </div>
      </div>

      {stock.score_breakdown && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6">
          <h2 className="text-base font-semibold text-slate-800 mb-4">점수 분석</h2>
          <ResponsiveContainer width="100%" height={240}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="subject" tick={{ fontSize: 11 }} />
              <Radar dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
            </RadarChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {Object.entries(stock.score_breakdown).map(([key, val]) => (
              <div key={key} className="flex items-center gap-2 text-sm">
                <span className="w-24 text-slate-500 text-right shrink-0">
                  {BREAKDOWN_LABELS[key] ?? key}
                </span>
                <div className="flex-1 bg-slate-100 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${Math.min((val as number) / 25 * 100, 100)}%` }}
                  />
                </div>
                <span className="text-slate-700 font-medium w-6 text-right">{val as number}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4">
        <div>
          <h2 className="text-base font-semibold text-slate-800 mb-2">추천 사유</h2>
          <p className="text-sm text-slate-600 leading-relaxed">{stock.reason}</p>
        </div>
        <div>
          <h2 className="text-base font-semibold text-red-600 mb-2">주요 리스크</h2>
          <p className="text-sm text-slate-600 leading-relaxed">{stock.risk_factor}</p>
        </div>
      </div>
    </div>
  );
}
