import { Currency } from "@/types";
import clsx from "clsx";

const FLAG_HINT: Record<Currency, string> = {
  MZN: "MZ",
  USD: "US",
  EUR: "EU",
  BRL: "BR",
  GBP: "GB",
  ZAR: "ZA",
};

export function CurrencyBadge({ currency, className }: { currency: Currency; className?: string }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full bg-ocean-700/60 px-2.5 py-1 text-xs font-medium text-sand-200",
        className
      )}
    >
      <span className="rounded-sm bg-sunset-400/20 px-1 text-[10px] font-mono text-sunset-300">
        {FLAG_HINT[currency]}
      </span>
      {currency}
    </span>
  );
}
