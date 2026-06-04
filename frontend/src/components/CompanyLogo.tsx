import type { JobPosting } from "../types";

type CompanyLogoProps = {
  job: JobPosting;
};

export function CompanyLogo({ job }: CompanyLogoProps) {
  return (
    <div className={`company-logo logo-${job.logoKind}`} aria-hidden="true">
      {job.logoKind === "letters" && "TQ"}
      {job.logoKind === "flag" && "ZEISS"}
    </div>
  );
}
