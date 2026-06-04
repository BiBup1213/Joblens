import { BookmarkPlus, CheckCircle2, CircleAlert, FilePlus2, Send } from "lucide-react";
import type { JobPosting } from "../types";

type ExpandedJobDetailsProps = {
  job: JobPosting;
};

export function ExpandedJobDetails({ job }: ExpandedJobDetailsProps) {
  return (
    <div className="expanded-details">
      <div className="analysis-grid">
        <section>
          <h3>Warum es passt</h3>
          <ul className="analysis-list positive">
            {job.reasons.map((reason) => (
              <li key={reason}>
                <CheckCircle2 aria-hidden="true" size={16} />
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h3>Was nicht gut passt</h3>
          <ul className="analysis-list caution">
            {job.gaps.map((gap) => (
              <li key={gap}>
                <CircleAlert aria-hidden="true" size={16} />
                <span>{gap}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <div className="next-step">
        <h3>Nächster Schritt</h3>
        <div className="next-step-row">
          <span>
            Aktueller Status: <strong>{job.status}</strong>
          </span>
          <div className="next-actions">
            <button type="button">
              <BookmarkPlus aria-hidden="true" size={16} />
              Status ändern
            </button>
            <button type="button">
              <Send aria-hidden="true" size={16} />
              Als beworben markieren
            </button>
            <button type="button">
              <FilePlus2 aria-hidden="true" size={16} />
              Notiz hinzufügen
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
