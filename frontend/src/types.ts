export type FitLevel =
  | "Passt nicht so gut"
  | "Passt teilweise"
  | "Passt gut"
  | "Passt sehr gut"
  | "Passt hervorragend";

export type BackendFitLevel =
  | "not_so_good"
  | "partial"
  | "good"
  | "very_good"
  | "excellent";

export type ApplicationStatus =
  | "Gespeichert"
  | "Prüfen"
  | "Offen"
  | "Beworben"
  | "Gespräch"
  | "Absage"
  | "Archiviert";

export type BackendApplicationStatus =
  | "saved"
  | "review"
  | "open"
  | "applied"
  | "interview"
  | "rejected"
  | "archived";

export type SourcePlatform =
  | "StepStone"
  | "LinkedIn"
  | "Arbeitsagentur"
  | "XING"
  | "Indeed"
  | "Other";

export type BackendSourcePlatform =
  | "stepstone"
  | "linkedin"
  | "arbeitsagentur"
  | "xing"
  | "indeed"
  | "other";

export type Skill = {
  id?: string;
  name: string;
  kind?: "strength" | "missing";
};

export type JobPosting = {
  id: string;
  company: string;
  title: string;
  location: string;
  source: SourcePlatform;
  status: ApplicationStatus;
  fit: FitLevel;
  strengths: Skill[];
  missing: Skill[];
  logoKind: "cube" | "letters" | "ribbon" | "triangle" | "flag";
  reasons: string[];
  gaps: string[];
  backendStatus?: BackendApplicationStatus;
};

export type BackendJobSkill = {
  id: number;
  name: string;
  kind: "strength" | "missing";
  kind_label?: string;
};

export type BackendJobAnalysis = {
  why_it_fits: string[];
  what_does_not_fit: string[];
  next_step_note: string;
};

export type BackendJobPosting = {
  id: number;
  company_name: string;
  job_title: string;
  location: string;
  work_model: string;
  source_platform: BackendSourcePlatform;
  source_platform_label?: SourcePlatform;
  source_url: string;
  raw_text?: string;
  application_status: BackendApplicationStatus;
  application_status_label?: ApplicationStatus;
  fit_level: BackendFitLevel;
  fit_level_label?: FitLevel;
  strengths: BackendJobSkill[];
  missing_skills: BackendJobSkill[];
  analysis: BackendJobAnalysis | null;
  created_at: string;
  updated_at: string;
};
