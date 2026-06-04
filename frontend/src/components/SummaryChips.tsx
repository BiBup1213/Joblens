import type { LucideIcon } from "lucide-react";

type SummaryItem = {
  label: string;
  icon: LucideIcon;
  tone?: "default" | "warm";
};

type SummaryChipsProps = {
  items: SummaryItem[];
};

export function SummaryChips({ items }: SummaryChipsProps) {
  return (
    <div className="summary-chips" aria-label="Zusammenfassung">
      {items.map((item) => {
        const Icon = item.icon;

        return (
          <span
            className={`summary-chip ${
              item.tone === "warm" ? "summary-chip-warm" : ""
            }`}
            key={item.label}
          >
            <Icon aria-hidden="true" size={19} />
            {item.label}
          </span>
        );
      })}
    </div>
  );
}
