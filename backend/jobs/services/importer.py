from dataclasses import dataclass
from urllib.parse import urlparse

from jobs.models import (
    ApplicationStatus,
    FitLevel,
    JobAnalysis,
    JobPosting,
    JobSkill,
    SkillKind,
    SourcePlatform,
)


@dataclass(frozen=True)
class ImportResult:
    job: JobPosting


def import_job_from_link(url: str) -> ImportResult:
    source_platform = detect_source_platform(url)
    company_name, job_title = placeholder_title_for_source(source_platform)

    job = JobPosting.objects.create(
        company_name=company_name,
        job_title=job_title,
        location="",
        work_model="",
        source_platform=source_platform,
        source_url=url,
        application_status=ApplicationStatus.SAVED,
        fit_level=FitLevel.GOOD,
    )
    attach_placeholder_analysis(job)
    return ImportResult(job=job)


def import_job_from_text(text: str) -> ImportResult:
    job = JobPosting.objects.create(
        company_name="Unbekanntes Unternehmen",
        job_title="Importierte Stelle",
        raw_text=text,
        source_platform=SourcePlatform.OTHER,
        application_status=ApplicationStatus.REVIEW,
        fit_level=FitLevel.PARTIAL,
    )
    attach_placeholder_analysis(job)
    return ImportResult(job=job)


def import_jobs_from_links(urls: list[str]) -> list[ImportResult]:
    return [import_job_from_link(url) for url in urls]


def detect_source_platform(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    domain = hostname.lower()

    if "stepstone" in domain:
        return SourcePlatform.STEPSTONE
    if "linkedin" in domain:
        return SourcePlatform.LINKEDIN
    if "arbeitsagentur" in domain:
        return SourcePlatform.ARBEITSAGENTUR
    if "xing" in domain:
        return SourcePlatform.XING
    if "indeed" in domain:
        return SourcePlatform.INDEED
    return SourcePlatform.OTHER


def placeholder_title_for_source(source_platform: str) -> tuple[str, str]:
    labels = dict(SourcePlatform.choices)
    label = labels.get(source_platform, "Other")
    return f"{label} Import", "Importierte Stelle"


def attach_placeholder_analysis(job: JobPosting) -> None:
    # TODO: Replace this placeholder with extraction and AI-assisted profile matching.
    for name in ["Python", "REST", "Backend"]:
        JobSkill.objects.create(job=job, name=name, kind=SkillKind.STRENGTH)
    for name in ["Cloud", "CI/CD"]:
        JobSkill.objects.create(job=job, name=name, kind=SkillKind.MISSING)

    JobAnalysis.objects.create(
        job=job,
        why_it_fits=[
            "Die importierte Stelle enthält erste Hinweise auf passende Backend-Erfahrung.",
            "Die Passform wurde vorläufig aus Platzhalterdaten erstellt.",
        ],
        what_does_not_fit=[
            "Die genaue Anforderungsliste wurde noch nicht extrahiert.",
            "Profilabgleich und Quellenanalyse folgen in einem späteren Schritt.",
        ],
        next_step_note="Import prüfen und bei Bedarf Status ändern.",
    )
