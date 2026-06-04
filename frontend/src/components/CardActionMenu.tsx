import {
  Archive,
  BookmarkPlus,
  BriefcaseBusiness,
  CalendarCheck,
  Send,
} from "lucide-react";
import type { BackendApplicationStatus } from "../types";

const actions = [
  { label: "Status ändern", icon: BookmarkPlus, status: "review" },
  { label: "Als beworben markieren", icon: Send, status: "applied" },
  { label: "Als offen markieren", icon: BriefcaseBusiness, status: "open" },
  { label: "Gespräch geplant", icon: CalendarCheck, status: "interview" },
  { label: "Archivieren", icon: Archive, status: "archived" },
] satisfies Array<{
  label: string;
  icon: typeof BookmarkPlus;
  status: BackendApplicationStatus;
}>;

type CardActionMenuProps = {
  onStatusChange: (status: BackendApplicationStatus) => void;
};

export function CardActionMenu({ onStatusChange }: CardActionMenuProps) {
  return (
    <div className="card-action-menu" role="menu" aria-label="Kartenaktionen">
      {actions.map((action) => {
        const Icon = action.icon;

        return (
          <button
            key={action.label}
            role="menuitem"
            type="button"
            onClick={() => onStatusChange(action.status)}
          >
            <Icon aria-hidden="true" size={17} />
            {action.label}
          </button>
        );
      })}
    </div>
  );
}
