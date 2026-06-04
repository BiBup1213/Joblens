import { BriefcaseBusiness } from "lucide-react";
import type { SourcePlatform } from "../types";

type SourceBadgeProps = {
  source: SourcePlatform;
};

export function SourceBadge({ source }: SourceBadgeProps) {
  return (
    <div className="source-badge">
      <span className={`source-icon source-${source.toLowerCase()}`}>
        {source === "LinkedIn" ? "in" : source === "Arbeitsagentur" ? "A" : ""}
        {source === "StepStone" && (
          <BriefcaseBusiness aria-hidden="true" size={14} />
        )}
      </span>
      {source}
    </div>
  );
}
