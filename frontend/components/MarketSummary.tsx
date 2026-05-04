import MarketCard from "./MarketCard";
import type { MarketSummary as MS } from "@/types";

interface Props {
  summary: MS & Record<string, number>;
  market: "us" | "kr";
}

export default function MarketSummary({ summary: m, market }: Props) {
  const items = market === "kr"
    ? [
        { label: "KOSPI",   value: m.kospi ?? 0,   sub: m.kospi_value?.toLocaleString("ko-KR", { maximumFractionDigits: 2 }) },
        { label: "KOSDAQ",  value: m.kosdaq ?? 0,   sub: m.kosdaq_value?.toLocaleString("ko-KR", { maximumFractionDigits: 2 }) },
        { label: "USD/KRW", value: m.usd_krw ?? 0,  sub: m.usd_krw_value ? `${Math.round(m.usd_krw_value).toLocaleString()}원` : undefined },
        { label: "VIX",     value: m.vix ?? 20,     isAbsolute: true, unit: "" },
      ]
    : [
        { label: "Nasdaq",  value: m.nasdaq ?? 0 },
        { label: "S&P 500", value: m.sp500 ?? 0 },
        { label: "Dow",     value: m.dow ?? 0 },
        { label: "Russell", value: m.russell ?? 0 },
        { label: "VIX",     value: m.vix ?? 20,   isAbsolute: true, unit: "" },
        { label: "10Y",     value: m.tnx ?? 4.3,  isAbsolute: true, unit: "%" },
      ];

  return (
    <div className="flex flex-wrap gap-x-8 gap-y-3 py-4 border-y border-slate-100">
      {items.map((item) => (
        <MarketCard key={item.label} {...item} />
      ))}
    </div>
  );
}
