import { Bookmark, BriefcaseBusiness, CircleDot, MessageCircle, XCircle } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import type { ApplicationStatus } from "../types";

const statusConfig: Record<
  ApplicationStatus,
  { className: string; Icon: LucideIcon }
> = {
  Gespeichert: { className: "status-saved", Icon: Bookmark },
  Prüfen: { className: "status-review", Icon: CircleDot },
  Offen: { className: "status-open", Icon: CircleDot },
  Beworben: { className: "status-applied", Icon: CircleDot },
  Gespräch: { className: "status-interview", Icon: MessageCircle },
  Absage: { className: "status-rejected", Icon: XCircle },
  Archiviert: { className: "status-archived", Icon: BriefcaseBusiness },
};

type StatusBadgeProps = {
  status: ApplicationStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const { className, Icon } = statusConfig[status];

  return (
    <span className={`status-badge ${className}`}>
      <Icon aria-hidden="true" size={14} />
      {status}
    </span>
  );
}
