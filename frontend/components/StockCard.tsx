import type { Stock } from "@/types";
import clsx from "clsx";

const isKR = (ticker: string) => ticker.endsWith(".KS") || ticker.endsWith(".KQ");

function fmtPrice(price: number, kr: boolean) {
  return kr ? `₩${Math.round(price).toLocaleString("ko-KR")}` : `$${price}`;
}

export default function StockCard({ stock }: { stock: Stock }) {
  const kr = isKR(stock.ticker);
  const displayTicker = kr ? stock.ticker.replace(/\.(KS|KQ)$/, "") : stock.ticker;
  const detailUrl = `/stock/${encodeURIComponent(stock.ticker)}?date=${stock.report_date}${kr ? "&market=kr" : ""}`;
  const scoreColor =
    stock.score >= 80 ? "text-green-600" : stock.score >= 60 ? "text-yellow-600" : "text-red-500";

  return (
    <a href={detailUrl} className="block py-3 border-b border-slate-100 last:border-0 hover:bg-slate-50 -mx-2 px-2 rounded transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline gap-2">
            <span className="font-semibold text-slate-900">{displayTicker}</span>
            <span className="text-xs text-slate-400 truncate">{stock.company_name}</span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5 line-clamp-1 leading-relaxed">{stock.reason}</p>
          <div className="flex gap-3 mt-1.5 text-xs text-slate-500">
            <span>매수 <span className="font-medium text-slate-700">{fmtPrice(stock.buy_price, kr)}</span></span>
            <span className="text-green-600">목표 {fmtPrice(stock.target_price, kr)}</span>
            <span className="text-red-500">손절 {fmtPrice(stock.stop_price, kr)}</span>
          </div>
        </div>
        <div className={clsx("text-xl font-bold tabular-nums shrink-0", scoreColor)}>
          {stock.score}
        </div>
      </div>
    </a>
  );
}
