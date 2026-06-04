from dataclasses import dataclass
from urllib.parse import urlparse

from jobs.models import (
    ApplicationStatus,
    FitLevel,
    JobAnalysis,
    JobPosting,
    SourcePlatform,
)


@dataclass(frozen=True)
class ImportResult:
    job: JobPosting


def import_job_from_link(url: str) -> ImportResult:
    source_platform = detect_source_platform(url)

    # TODO: Replace this placeholder with real extraction/parsing once available.
    job = JobPosting.objects.create(
        company_name="Unbekanntes Unternehmen",
        job_title="Importierte Stellenanzeige",
        location="",
        work_model="",
        source_platform=source_platform,
        source_url=url,
        application_status=ApplicationStatus.SAVED,
        fit_level=FitLevel.PARTIAL,
    )
    attach_empty_placeholder_analysis(job)
    return ImportResult(job=job)


def import_job_from_text(text: str) -> ImportResult:
    job = JobPosting.objects.create(
        company_name="Unbekanntes Unternehmen",
        job_title="Importierte Stellenanzeige",
        raw_text=text,
        source_platform=SourcePlatform.OTHER,
        application_status=ApplicationStatus.SAVED,
        fit_level=FitLevel.PARTIAL,
    )
    attach_empty_placeholder_analysis(job)
    return ImportResult(job=job)


def import_jobs_from_links(urls: list[str]) -> list[ImportResult]:
    return [import_job_from_link(url) for url in urls]


def detect_source_platform(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    domain = hostname.lower()

    if domain == "stepstone.de" or domain.endswith(".stepstone.de"):
        return SourcePlatform.STEPSTONE
    if domain == "linkedin.com" or domain.endswith(".linkedin.com"):
        return SourcePlatform.LINKEDIN
    if domain == "arbeitsagentur.de" or domain.endswith(".arbeitsagentur.de"):
        return SourcePlatform.ARBEITSAGENTUR
    if domain == "xing.com" or domain.endswith(".xing.com"):
        return SourcePlatform.XING
    if domain == "indeed.com" or domain.endswith(".indeed.com"):
        return SourcePlatform.INDEED
    return SourcePlatform.OTHER


def attach_empty_placeholder_analysis(job: JobPosting) -> None:
    JobAnalysis.objects.create(
        job=job,
        why_it_fits=[],
        what_does_not_fit=[],
        next_step_note="Importiert. Extraktion und Profilabgleich stehen noch aus.",
    )
