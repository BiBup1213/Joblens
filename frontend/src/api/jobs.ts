import type {
  ApplicationStatus,
  BackendApplicationStatus,
  BackendFitLevel,
  BackendJobAnalysis,
  BackendJobPosting,
  BackendJobSkill,
  BackendSourcePlatform,
  FitLevel,
  JobPosting,
  SourcePlatform,
} from "../types";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export const statusLabels: Record<BackendApplicationStatus, ApplicationStatus> = {
  saved: "Gespeichert",
  review: "Prüfen",
  open: "Offen",
  applied: "Beworben",
  interview: "Gespräch",
  rejected: "Absage",
  archived: "Archiviert",
};

const fitLabels: Record<BackendFitLevel, FitLevel> = {
  not_so_good: "Passt nicht so gut",
  partial: "Passt teilweise",
  good: "Passt gut",
  very_good: "Passt sehr gut",
  excellent: "Passt hervorragend",
};

const sourceLabels: Record<BackendSourcePlatform, SourcePlatform> = {
  stepstone: "StepStone",
  linkedin: "LinkedIn",
  arbeitsagentur: "Arbeitsagentur",
  xing: "XING",
  indeed: "Indeed",
  other: "Other",
};

export const statusToBackend: Record<ApplicationStatus, BackendApplicationStatus> = {
  Gespeichert: "saved",
  Prüfen: "review",
  Offen: "open",
  Beworben: "applied",
  Gespräch: "interview",
  Absage: "rejected",
  Archiviert: "archived",
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `API request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getJobs(): Promise<JobPosting[]> {
  const jobs = await request<BackendJobPosting[] | { results: BackendJobPosting[] }>(
    "/jobs/",
  );
  const results = Array.isArray(jobs) ? jobs : jobs.results;
  return results.map(mapBackendJob);
}

export async function getJob(id: string): Promise<JobPosting> {
  const job = await request<BackendJobPosting>(`/jobs/${id}/`);
  return mapBackendJob(job);
}

export async function updateJobStatus(
  id: string,
  applicationStatus: BackendApplicationStatus,
): Promise<JobPosting> {
  const job = await request<BackendJobPosting>(`/jobs/${id}/change-status/`, {
    method: "POST",
    body: JSON.stringify({ application_status: applicationStatus }),
  });
  return mapBackendJob(job);
}

export async function importJobLink(url: string): Promise<JobPosting> {
  const job = await request<BackendJobPosting>("/jobs/import-link/", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
  return mapBackendJob(job);
}

export async function importJobText(text: string): Promise<JobPosting> {
  const job = await request<BackendJobPosting>("/jobs/import-text/", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
  return mapBackendJob(job);
}

export async function importBulkJobLinks(urls: string[]): Promise<JobPosting[]> {
  const jobs = await request<BackendJobPosting[]>("/jobs/import-bulk/", {
    method: "POST",
    body: JSON.stringify({ urls }),
  });
  return jobs.map(mapBackendJob);
}

function mapBackendJob(job: BackendJobPosting): JobPosting {
  return {
    id: String(job.id),
    company: job.company_name,
    title: job.job_title,
    location: formatLocation(job.location, job.work_model),
    source: getSourceLabel(job),
    status: getStatusLabel(job),
    fit: getFitLabel(job),
    strengths: job.strengths.map(mapSkill),
    missing: job.missing_skills.map(mapSkill),
    logoKind: inferLogoKind(job),
    reasons: getAnalysisList(job.analysis, "why_it_fits"),
    gaps: getAnalysisList(job.analysis, "what_does_not_fit"),
    backendStatus: job.application_status,
  };
}

function mapSkill(skill: BackendJobSkill) {
  return { id: String(skill.id), name: skill.name, kind: skill.kind };
}

function formatLocation(location: string, workModel: string) {
  if (location && workModel && location !== workModel) {
    return `${location} · ${workModel}`;
  }
  return location || workModel || "Ort offen";
}

function getStatusLabel(job: BackendJobPosting): ApplicationStatus {
  return job.application_status_label ?? statusLabels[job.application_status];
}

function getFitLabel(job: BackendJobPosting): FitLevel {
  return job.fit_level_label ?? fitLabels[job.fit_level];
}

function getSourceLabel(job: BackendJobPosting): SourcePlatform {
  return job.source_platform_label ?? sourceLabels[job.source_platform] ?? "Other";
}

function getAnalysisList(
  analysis: BackendJobAnalysis | null,
  key: keyof Pick<BackendJobAnalysis, "why_it_fits" | "what_does_not_fit">,
) {
  return analysis?.[key] ?? [];
}

function inferLogoKind(job: BackendJobPosting): JobPosting["logoKind"] {
  const company = job.company_name.toLowerCase();

  if (company.includes("teqyard")) {
    return "letters";
  }
  if (company.includes("rheinmetall")) {
    return "ribbon";
  }
  if (company.includes("msg")) {
    return "triangle";
  }
  if (company.includes("zeiss")) {
    return "flag";
  }
  return "cube";
}
