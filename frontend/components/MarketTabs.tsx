import clsx from "clsx";
import Link from "next/link";

interface Props {
  active: "us" | "kr";
  basePath?: string;
}

export default function MarketTabs({ active, basePath = "/" }: Props) {
  return (
    <div className="flex gap-1 text-sm">
      {(["us", "kr"] as const).map((m) => (
        <Link
          key={m}
          href={`${basePath}?market=${m}`}
          className={clsx(
            "px-3 py-1 rounded-md font-medium transition-colors",
            active === m
              ? "bg-slate-900 text-white"
              : "text-slate-400 hover:text-slate-700"
          )}
        >
          {m === "us" ? "🇺🇸 US" : "🇰🇷 KR"}
        </Link>
      ))}
    </div>
  );
}
