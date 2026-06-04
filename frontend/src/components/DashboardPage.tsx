import { Bookmark, ClipboardPlus, Inbox, Send, Star } from "lucide-react";
import { useState } from "react";
import type { BackendApplicationStatus, JobPosting } from "../types";
import { FilterChips } from "./FilterChips";
import { FloatingAddButton } from "./FloatingAddButton";
import { JobCard } from "./JobCard";
import { Sidebar } from "./Sidebar";
import { SummaryChips } from "./SummaryChips";

type DashboardPageProps = {
  jobs: JobPosting[];
  isLoading: boolean;
  errorMessage: string | null;
  pendingStatusJobIds: string[];
  onAddJob: () => void;
  onRetry: () => void;
  onStatusChange: (jobId: string, status: BackendApplicationStatus) => void;
};

export function DashboardPage({
  jobs,
  isLoading,
  errorMessage,
  pendingStatusJobIds,
  onAddJob,
  onRetry,
  onStatusChange,
}: DashboardPageProps) {
  const [expandedJobId, setExpandedJobId] = useState<string>("");
  const [openMenuJobId, setOpenMenuJobId] = useState<string | null>(null);

  const savedCount = jobs.filter((job) => job.status === "Gespeichert").length;
  const goodMatchCount = jobs.filter((job) =>
    ["Passt gut", "Passt sehr gut", "Passt hervorragend"].includes(job.fit),
  ).length;
  const openCount = jobs.filter((job) => job.status === "Offen").length;

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="dashboard">
        <div className="dashboard-top">
          <div>
            <h1>Deine Stellen</h1>
            <SummaryChips
              items={[
                { label: `${savedCount} gespeichert`, icon: Bookmark },
                { label: `${goodMatchCount} gute Matches`, icon: Star },
                { label: `${openCount} offen`, icon: Inbox, tone: "warm" },
              ]}
            />
          </div>
          <button className="secondary-action" type="button">
            <ClipboardPlus aria-hidden="true" size={19} />
            Zwischenablage importieren
          </button>
        </div>

        <FilterChips
          filters={[
            { label: "Alle", active: true },
            { label: "Gute Matches", icon: Star },
            { label: "Offen", icon: Inbox },
            { label: "Beworben", icon: Send },
            { label: "Archiviert", icon: Bookmark },
          ]}
        />

        {isLoading && (
          <div className="dashboard-state" role="status">
            Stellen werden geladen...
          </div>
        )}

        {!isLoading && errorMessage && jobs.length === 0 && (
          <div className="dashboard-state dashboard-state-error" role="alert">
            <span>Die Stellen konnten nicht geladen werden.</span>
            <button type="button" onClick={onRetry}>
              Erneut versuchen
            </button>
          </div>
        )}

        {!isLoading && !errorMessage && jobs.length === 0 && (
          <div className="dashboard-state dashboard-empty-state">
            <div>
              <h2>Noch keine Stellen gespeichert</h2>
              <p>Füge deine erste Stellenanzeige per Link, Text oder Datei hinzu.</p>
            </div>
            <button type="button" onClick={onAddJob}>
              Stelle hinzufügen
            </button>
          </div>
        )}

        {!isLoading && errorMessage && jobs.length > 0 && (
          <div className="dashboard-state dashboard-state-error dashboard-state-inline" role="alert">
            <span>{errorMessage}</span>
            <button type="button" onClick={onRetry}>
              Aktualisieren
            </button>
          </div>
        )}

        {!isLoading && jobs.length > 0 && (
          <section className="job-grid" aria-label="Stellenkarten">
            {jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                isExpanded={expandedJobId === job.id}
                isMenuOpen={openMenuJobId === job.id}
                onToggleDetails={() =>
                  setExpandedJobId((current) =>
                    current === job.id ? "" : job.id,
                  )
                }
                onToggleMenu={() =>
                  setOpenMenuJobId((current) =>
                    current === job.id ? null : job.id,
                  )
                }
                onStatusChange={(status) => {
                  setOpenMenuJobId(null);
                  onStatusChange(job.id, status);
                }}
                isStatusUpdating={pendingStatusJobIds.includes(job.id)}
              />
            ))}
          </section>
        )}
      </main>
      <FloatingAddButton onClick={onAddJob} />
    </div>
  );
}
