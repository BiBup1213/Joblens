from dataclasses import dataclass
import logging
from typing import Any

from jobs.models import (
    ApplicationStatus,
    FitLevel,
    JobAnalysis,
    JobPosting,
    JobSkill,
    SkillKind,
)
from jobs.services.source_platform import detect_source_platform
from jobs.services.text_importer import extract_job_from_text


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ImportResult:
    job: JobPosting


def import_job_from_link(url: str) -> ImportResult:
    logger.info("JobLens import-link called")
    source_platform = detect_source_platform(url)

    try:
        from jobs.services.link_importer import fetch_job_text_from_url

        link_result = fetch_job_text_from_url(url)
    except Exception:
        logger.exception("JobLens import-link extraction failed before fallback")
        job = create_link_placeholder_job(url, source_platform)
        return ImportResult(job=job)

    if link_result.has_useful_text:
        logger.info("JobLens import-link extraction succeeded")
        try:
            job = create_job_from_text_data(
                text=link_result.extracted_text,
                source_platform=link_result.source_platform,
                source_url=url,
                metadata=link_result.metadata,
            )
            return ImportResult(job=job)
        except Exception:
            logger.exception("JobLens import-link text pipeline failed after extraction")

    logger.info(
        "JobLens import-link falling back: %s",
        link_result.error or link_result.diagnostics.get("fallback_reason", ""),
    )
    job = create_link_placeholder_job(url, link_result.source_platform)
    return ImportResult(job=job)


def create_link_placeholder_job(url: str, source_platform: str) -> JobPosting:
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
    attach_link_fallback_analysis(job)
    return job


def import_job_from_text(text: str) -> ImportResult:
    logger.info("JobLens import-text called")
    try:
        job = create_job_from_text_data(text=text)
    except Exception:
        logger.exception("JobLens import-text extraction failed before fallback")
        job = create_text_placeholder_job(text)
    return ImportResult(job=job)


def create_text_placeholder_job(text: str) -> JobPosting:
    job = JobPosting.objects.create(
        company_name="Unbekanntes Unternehmen",
        job_title="Importierte Stellenanzeige",
        location="",
        work_model="",
        raw_text=text,
        application_status=ApplicationStatus.SAVED,
        fit_level=FitLevel.PARTIAL,
    )
    JobAnalysis.objects.create(
        job=job,
        why_it_fits=[
            "Die Stellenanzeige wurde gespeichert, konnte aber noch nicht automatisch ausgewertet werden."
        ],
        what_does_not_fit=[
            "Der eingefügte Text konnte nicht zuverlässig ausgewertet werden."
        ],
        next_step_note="Text prüfen",
    )
    return job


def create_job_from_text_data(
    text: str,
    source_platform: str | None = None,
    source_url: str = "",
    metadata: Any | None = None,
) -> JobPosting:
    extracted = extract_job_from_text(text)

    job = JobPosting.objects.create(
        company_name=get_metadata_value(metadata, "company_name") or extracted["company_name"],
        job_title=get_metadata_value(metadata, "job_title") or extracted["job_title"],
        location=get_metadata_value(metadata, "location") or extracted["location"],
        work_model=get_metadata_value(metadata, "work_model") or extracted["work_model"],
        raw_text=text,
        source_platform=source_platform or extracted["source_platform"],
        source_url=source_url,
        application_status=ApplicationStatus.SAVED,
        fit_level=extracted["fit_level"],
    )
    attach_detected_skills(job, extracted["strengths"], SkillKind.STRENGTH)
    attach_detected_skills(job, extracted["missing_skills"], SkillKind.MISSING)
    JobAnalysis.objects.create(
        job=job,
        why_it_fits=extracted["why_it_fits"],
        what_does_not_fit=extracted["what_does_not_fit"],
        next_step_note=extracted["next_step_note"],
    )
    logger.info(
        "JobLens text extraction created job id=%s strengths=%s missing=%s",
        job.id,
        len(extracted["strengths"]),
        len(extracted["missing_skills"]),
    )
    return job


def import_jobs_from_links(urls: list[str]) -> list[ImportResult]:
    return [import_job_from_link(url) for url in urls]


def attach_link_fallback_analysis(job: JobPosting) -> None:
    JobAnalysis.objects.create(
        job=job,
        why_it_fits=[
            "Die Stellenanzeige wurde gespeichert, konnte aber noch nicht automatisch ausgewertet werden."
        ],
        what_does_not_fit=[
            "Der Inhalt der Seite konnte nicht zuverlässig ausgelesen werden. Bitte füge den Text der Anzeige manuell ein, um eine bessere Bewertung zu erhalten."
        ],
        next_step_note="Text manuell ergänzen",
    )


def attach_detected_skills(job: JobPosting, skills: list[str], kind: str) -> None:
    seen = set()
    for skill in skills:
        normalized = skill.strip()
        if not normalized or normalized.lower() in seen:
            continue
        seen.add(normalized.lower())
        JobSkill.objects.create(job=job, name=normalized, kind=kind)


def get_metadata_value(metadata: Any | None, field_name: str) -> str:
    if metadata is None:
        return ""
    value = getattr(metadata, field_name, "")
    return value if isinstance(value, str) else ""
