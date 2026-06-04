import { Blocks } from "lucide-react";
import type { LucideIcon } from "lucide-react";

type FilterItem = {
  label: string;
  active?: boolean;
  icon?: LucideIcon;
};

type FilterChipsProps = {
  filters: FilterItem[];
};

export function FilterChips({ filters }: FilterChipsProps) {
  return (
    <div className="filter-chips" aria-label="Filter">
      {filters.map((filter) => {
        const Icon = filter.icon ?? Blocks;

        return (
          <button
            className={`filter-chip${filter.active ? " is-active" : ""}`}
            key={filter.label}
            type="button"
          >
            <Icon aria-hidden="true" size={19} />
            {filter.label}
          </button>
        );
      })}
    </div>
  );
}
