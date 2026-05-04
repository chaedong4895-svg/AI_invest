import type { NewsItem } from "@/types";
import clsx from "clsx";

const DOT: Record<string, string> = {
  positive: "bg-green-500",
  negative: "bg-red-500",
  neutral:  "bg-slate-300",
};

export default function NewsCard({ item }: { item: NewsItem }) {
  return (
    <div className="flex gap-3 py-3 border-b border-slate-100 last:border-0">
      <span className={clsx("mt-1.5 w-1.5 h-1.5 rounded-full shrink-0", DOT[item.sentiment] ?? DOT.neutral)} />
      <div className="min-w-0">
        <div className="flex items-center gap-2 mb-0.5">
          {item.source && <span className="text-xs text-slate-400">{item.source}</span>}
          {item.sector && <span className="text-xs text-blue-500">{item.sector}</span>}
        </div>
        <a
          href={item.url ?? "#"}
          target="_blank"
          rel="noreferrer"
          className="text-sm font-medium text-slate-800 hover:text-blue-600 line-clamp-1 block"
        >
          {item.title}
        </a>
        <p className="text-xs text-slate-500 mt-0.5 line-clamp-2 leading-relaxed">{item.summary}</p>
      </div>
    </div>
  );
}
