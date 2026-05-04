import type { RiskLevel } from "@/types";
import clsx from "clsx";

const CONFIG: Record<RiskLevel, { dot: string; text: string; msg: string }> = {
  "Risk-On":  { dot: "bg-green-500", text: "text-green-700", msg: "적극 매수 고려" },
  Neutral:    { dot: "bg-yellow-400", text: "text-yellow-700", msg: "선별적 접근" },
  "Risk-Off": { dot: "bg-red-500",   text: "text-red-700",   msg: "현금 비중 확대" },
};

export default function RiskBadge({ level }: { level: RiskLevel }) {
  const cfg = CONFIG[level];
  return (
    <div className="flex items-center gap-2">
      <span className={clsx("w-2.5 h-2.5 rounded-full inline-block", cfg.dot)} />
      <span className={clsx("font-semibold text-sm", cfg.text)}>
        {level}
      </span>
      <span className="text-slate-400 text-sm">— {cfg.msg}</span>
    </div>
  );
}
