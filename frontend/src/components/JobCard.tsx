import { MapPin, MoreVertical } from "lucide-react";
import type { BackendApplicationStatus, JobPosting } from "../types";
import { CardActionMenu } from "./CardActionMenu";
import { CompanyLogo } from "./CompanyLogo";
import { ExpandedJobDetails } from "./ExpandedJobDetails";
import { FitScale } from "./FitScale";
import { SkillChip } from "./SkillChip";
import { SourceBadge } from "./SourceBadge";
import { StatusBadge } from "./StatusBadge";

type JobCardProps = {
  job: JobPosting;
  isExpanded: boolean;
  isMenuOpen: boolean;
  onToggleDetails: () => void;
  onToggleMenu: () => void;
  onStatusChange: (status: BackendApplicationStatus) => void;
  isStatusUpdating: boolean;
};

export function JobCard({
  job,
  isExpanded,
  isMenuOpen,
  onToggleDetails,
  onToggleMenu,
  onStatusChange,
  isStatusUpdating,
}: JobCardProps) {
  return (
    <article
      className={`job-card${isExpanded ? " is-expanded" : ""}`}
      onClick={onToggleDetails}
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onToggleDetails();
        }
      }}
    >
      <div className="card-header">
        <CompanyLogo job={job} />
        <div className="job-title-block">
          <h2>{job.company}</h2>
          <p>{job.title}</p>
          <span className="job-location">
            <MapPin aria-hidden="true" size={15} />
            {job.location}
          </span>
        </div>
        <div className="card-actions">
          <StatusBadge status={job.status} />
          <button
            className="icon-button"
            type="button"
            aria-label={`Aktionen für ${job.company}`}
            aria-expanded={isMenuOpen}
            disabled={isStatusUpdating}
            onClick={(event) => {
              event.stopPropagation();
              onToggleMenu();
            }}
          >
            <MoreVertical aria-hidden="true" size={21} />
          </button>
          {isMenuOpen && (
            <div onClick={(event) => event.stopPropagation()}>
              <CardActionMenu
                onStatusChange={onStatusChange}
                isDisabled={isStatusUpdating}
              />
            </div>
          )}
        </div>
      </div>

      <FitScale fit={job.fit} />

      <div className="skill-row">
        <span className="meta-label">Stärken</span>
        <div className="skill-list">
          {job.strengths.map((skill) => (
            <SkillChip key={skill.name} skill={skill} tone="strength" />
          ))}
        </div>
      </div>

      <div className="skill-row">
        <span className="meta-label">Fehlt</span>
        <div className="skill-list">
          {job.missing.map((skill) => (
            <SkillChip key={skill.name} skill={skill} tone="missing" />
          ))}
        </div>
      </div>

      <SourceBadge source={job.source} />

      {isExpanded && <ExpandedJobDetails job={job} />}
    </article>
  );
}
