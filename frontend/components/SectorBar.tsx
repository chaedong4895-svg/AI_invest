import type { SectorItem } from "@/types";
import clsx from "clsx";

export default function SectorBar({ bullish, bearish }: { bullish: SectorItem[]; bearish: SectorItem[] }) {
  return (
    <div>
      <div className="text-xs font-medium text-slate-400 uppercase tracking-wide mb-3">섹터</div>
      <div className="space-y-2">
        {[...bullish, ...bearish].map((item) => {
          const pos = item.change_pct >= 0;
          return (
            <div key={item.ticker} className="flex items-center justify-between text-sm">
              <span className="text-slate-600 text-xs">{item.name}</span>
              <span className={clsx("font-medium tabular-nums text-xs", pos ? "text-green-600" : "text-red-500")}>
                {pos ? "+" : ""}{item.change_pct.toFixed(2)}%
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
