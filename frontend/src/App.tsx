import { useCallback, useEffect, useState } from "react";
import type { BackendApplicationStatus, JobPosting } from "./types";
import { AddJobModal } from "./components/AddJobModal";
import { DashboardPage } from "./components/DashboardPage";
import {
  getJobs,
  importBulkJobLinks,
  importJobLink,
  importJobText,
  statusLabels,
  updateJobStatus,
} from "./api/jobs";

export default function App() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [pendingStatusJobIds, setPendingStatusJobIds] = useState<string[]>([]);

  const loadJobs = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      setJobs(await getJobs());
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Die Stellen konnten nicht geladen werden.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadJobs();
  }, [loadJobs]);

  async function handleStatusChange(
    jobId: string,
    status: BackendApplicationStatus,
  ) {
    if (pendingStatusJobIds.includes(jobId)) {
      return;
    }

    const previousJobs = jobs;
    setPendingStatusJobIds((ids) => [...ids, jobId]);
    setJobs((currentJobs) =>
      currentJobs.map((job) =>
        job.id === jobId
          ? { ...job, status: statusLabels[status], backendStatus: status }
          : job,
      ),
    );

    try {
      const updatedJob = await updateJobStatus(jobId, status);
      setJobs((currentJobs) =>
        currentJobs.map((job) => (job.id === jobId ? updatedJob : job)),
      );
      setErrorMessage(null);
    } catch (error) {
      setJobs(previousJobs);
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Der Status konnte nicht aktualisiert werden.",
      );
    } finally {
      setPendingStatusJobIds((ids) => ids.filter((id) => id !== jobId));
    }
  }

  async function handleImportLink(url: string) {
    const importedJob = await importJobLink(url);
    setJobs((currentJobs) => [importedJob, ...currentJobs]);
    setErrorMessage(null);
  }

  async function handleImportText(text: string) {
    const importedJob = await importJobText(text);
    setJobs((currentJobs) => [importedJob, ...currentJobs]);
    setErrorMessage(null);
  }

  async function handleImportBulk(urls: string[]) {
    const result = await importBulkJobLinks(urls);
    setJobs((currentJobs) => [...result.jobs, ...currentJobs]);
    setErrorMessage(
      result.errors.length > 0
        ? `${result.jobs.length} Stellen importiert, ${result.errors.length} Links konnten nicht verarbeitet werden.`
        : null,
    );
  }

  return (
    <>
      <DashboardPage
        jobs={jobs}
        isLoading={isLoading}
        errorMessage={errorMessage}
        pendingStatusJobIds={pendingStatusJobIds}
        onAddJob={() => setIsAddModalOpen(true)}
        onRetry={loadJobs}
        onStatusChange={handleStatusChange}
      />
      <AddJobModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onImportLink={handleImportLink}
        onImportText={handleImportText}
        onImportBulk={handleImportBulk}
      />
    </>
  );
}
