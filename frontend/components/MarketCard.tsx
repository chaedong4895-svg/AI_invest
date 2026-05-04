import clsx from "clsx";

interface Props {
  label: string;
  value: number;
  isAbsolute?: boolean;
  unit?: string;
  sub?: string;
}

export default function MarketCard({ label, value, isAbsolute = false, unit = "%", sub }: Props) {
  const positive = value >= 0;
  const display = isAbsolute
    ? `${value.toFixed(2)}${unit}`
    : `${positive ? "+" : ""}${value.toFixed(2)}${unit}`;

  return (
    <div>
      <div className="text-xs text-slate-400 mb-0.5">{label}</div>
      <div className={clsx(
        "text-base font-semibold tabular-nums",
        isAbsolute ? "text-slate-700" : positive ? "text-green-600" : "text-red-500"
      )}>
        {display}
      </div>
      {sub && <div className="text-xs text-slate-400 mt-0.5">{sub}</div>}
    </div>
  );
}
