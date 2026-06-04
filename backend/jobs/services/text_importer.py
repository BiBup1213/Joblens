from __future__ import annotations

import re
from typing import TypedDict

from jobs.models import FitLevel, SourcePlatform


class ExtractedJobData(TypedDict):
    company_name: str
    job_title: str
    location: str
    work_model: str
    source_platform: str
    fit_level: str
    strengths: list[str]
    missing_skills: list[str]
    why_it_fits: list[str]
    what_does_not_fit: list[str]
    next_step_note: str


TITLE_KEYWORDS = [
    "Machine Learning Engineer",
    "Softwareentwickler",
    "Software Engineer",
    "Python Developer",
    "Backend Developer",
    "Frontend Developer",
    "Fullstack Developer",
    "AI Consultant",
    "Data Scientist",
    "Entwickler",
    "Consultant",
]

KNOWN_LOCATIONS = [
    "Wolfsburg",
    "Braunschweig",
    "München",
    "Hamburg",
    "Berlin",
    "Köln",
    "Frankfurt",
    "Jena",
]

TECH_KEYWORDS = {
    "Python": ["python"],
    "Django": ["django"],
    "FastAPI": ["fastapi", "fast api"],
    "Flask": ["flask"],
    "REST": ["rest"],
    "API": ["api", "apis"],
    "TypeScript": ["typescript"],
    "JavaScript": ["javascript"],
    "React": ["react"],
    "Angular": ["angular"],
    "Node.js": ["node.js", "nodejs", "node js"],
    "SQL": ["sql"],
    "PostgreSQL": ["postgresql", "postgres"],
    "Docker": ["docker"],
    "Git": ["git"],
    "CI/CD": ["ci/cd", "cicd", "continuous integration"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Cloud": ["cloud"],
    "AWS": ["aws"],
    "Azure": ["azure"],
    "Java": ["java"],
    "Spring": ["spring"],
    "C#": ["c#"],
    "Go": ["go", "golang"],
    "MQTT": ["mqtt"],
    "Machine Learning": ["machine learning", "ml"],
    "Data Analysis": ["data analysis", "datenanalyse", "data analytics"],
}

STRONG_SKILLS = {
    "Python",
    "Django",
    "REST",
    "API",
    "React",
    "TypeScript",
    "SQL",
    "PostgreSQL",
    "Docker",
    "Git",
    "Machine Learning",
    "Data Analysis",
}

GAP_SKILLS = {
    "Go",
    "C#",
    "MQTT",
    "Kubernetes",
    "AWS",
    "Azure",
    "Spring",
    "Angular",
    "CI/CD",
    "Cloud",
}


def extract_job_from_text(raw_text: str) -> ExtractedJobData:
    """Extract first-pass job data with simple, replaceable heuristics.

    TODO: Replace or augment these deterministic rules with LLM-based extraction
    once JobLens introduces AI-assisted parsing and profile matching.
    """
    lines = normalize_lines(raw_text)
    detected_skills = detect_skills(raw_text)
    strengths = [skill for skill in detected_skills if skill in STRONG_SKILLS]
    missing_skills = [skill for skill in detected_skills if skill in GAP_SKILLS]
    location = detect_location(raw_text)
    work_model = detect_work_model(raw_text)

    return {
        "company_name": detect_company(lines),
        "job_title": detect_job_title(raw_text, lines),
        "location": location,
        "work_model": work_model,
        "source_platform": detect_source_platform_from_text(raw_text),
        "fit_level": calculate_fit_level(strengths, missing_skills),
        "strengths": strengths,
        "missing_skills": missing_skills,
        "why_it_fits": build_why_it_fits(strengths, work_model),
        "what_does_not_fit": build_what_does_not_fit(missing_skills),
        "next_step_note": "Automatisch aus eingefügtem Text vorstrukturiert.",
    }


def normalize_lines(raw_text: str) -> list[str]:
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def detect_job_title(raw_text: str, lines: list[str]) -> str:
    for line in lines[:8]:
        for title in TITLE_KEYWORDS:
            if title.lower() in line.lower():
                return title

    for title in TITLE_KEYWORDS:
        if title.lower() in raw_text.lower():
            return title

    return "Importierte Stellenanzeige"


def detect_company(lines: list[str]) -> str:
    legal_suffix_pattern = re.compile(
        r"([A-ZÄÖÜ][\wÄÖÜäöüß&.,+\- ]{1,80}?"
        r"(?:GmbH & Co\. KG|GmbH|AG|SE|UG))"
    )

    for line in lines[:20]:
        match = legal_suffix_pattern.search(line)
        if match:
            return clean_company_name(match.group(1))

    bei_pattern = re.compile(r"\bbei\s+([A-ZÄÖÜ][\wÄÖÜäöüß&.,+\- ]{2,80})", re.I)
    for line in lines[:20]:
        match = bei_pattern.search(line)
        if match:
            return clean_company_name(match.group(1))

    return "Unbekanntes Unternehmen"


def clean_company_name(value: str) -> str:
    return re.split(r"\s[-|–]\s|,|\s+sucht\b", value.strip(), maxsplit=1)[0].strip()


def detect_location(raw_text: str) -> str:
    lowered_text = raw_text.lower()
    for location in KNOWN_LOCATIONS:
        if location.lower() in lowered_text:
            return location

    if contains_any(lowered_text, ["remote", "remote-first", "remote first"]):
        return "Remote"

    return ""


def detect_work_model(raw_text: str) -> str:
    lowered_text = raw_text.lower()

    if contains_any(lowered_text, ["hybrid", "homeoffice tage", "remote und vor ort"]):
        return "Hybrid"
    if contains_any(lowered_text, ["remote", "remote-first", "remote first"]):
        return "Remote"
    if contains_any(lowered_text, ["vor ort", "onsite", "on-site", "büropräsenz"]):
        return "Vor Ort"
    if "homeoffice" in lowered_text:
        return "Hybrid"

    return ""


def detect_source_platform_from_text(raw_text: str) -> str:
    lowered_text = raw_text.lower()

    if "stepstone.de" in lowered_text:
        return SourcePlatform.STEPSTONE
    if "linkedin.com" in lowered_text:
        return SourcePlatform.LINKEDIN
    if "arbeitsagentur.de" in lowered_text:
        return SourcePlatform.ARBEITSAGENTUR
    if "xing.com" in lowered_text:
        return SourcePlatform.XING
    if "indeed.com" in lowered_text:
        return SourcePlatform.INDEED

    return SourcePlatform.OTHER


def detect_skills(raw_text: str) -> list[str]:
    detected = []
    lowered_text = raw_text.lower()

    for skill, aliases in TECH_KEYWORDS.items():
        if any(has_keyword(lowered_text, alias) for alias in aliases):
            detected.append(skill)

    return detected


def has_keyword(lowered_text: str, alias: str) -> bool:
    lowered_alias = alias.lower()
    if re.search(r"[^\w\s]", lowered_alias):
        return lowered_alias in lowered_text
    return re.search(rf"\b{re.escape(lowered_alias)}\b", lowered_text) is not None


def calculate_fit_level(strengths: list[str], missing_skills: list[str]) -> str:
    strength_count = len(strengths)
    gap_count = len(missing_skills)

    if strength_count >= 5 and gap_count <= 1:
        return FitLevel.EXCELLENT
    if strength_count >= 3 and gap_count <= 1:
        return FitLevel.VERY_GOOD
    if strength_count >= 2 and gap_count <= 3:
        return FitLevel.GOOD
    if gap_count >= 3 and strength_count <= 1:
        return FitLevel.NOT_SO_GOOD
    if strength_count <= 1 or gap_count >= 3:
        return FitLevel.PARTIAL

    return FitLevel.PARTIAL


def build_why_it_fits(strengths: list[str], work_model: str) -> list[str]:
    bullets = []

    if strengths:
        bullets.append(
            "Die Anzeige enthält Technologien, die bereits in deinem Profil stark sind."
        )
        bullets.append(f"{format_skill_list(strengths[:3])} passen gut zu deinem bisherigen Schwerpunkt.")

    if work_model:
        bullets.append("Das Arbeitsmodell passt grundsätzlich zu deinen Präferenzen.")

    if not bullets:
        bullets.append(
            "Die Stellenanzeige enthält noch zu wenig strukturierte Informationen für eine belastbare Bewertung."
        )

    return bullets[:3]


def build_what_does_not_fit(missing_skills: list[str]) -> list[str]:
    bullets = []

    if missing_skills:
        bullets.append(
            f"{format_skill_list(missing_skills[:3])} werden genannt, sind aber aktuell nicht stark in deinem Profil vertreten."
        )

    cloud_or_system_skills = {"Kubernetes", "AWS", "Azure", "Cloud", "CI/CD"}
    if any(skill in cloud_or_system_skills for skill in missing_skills):
        bullets.append("Ein Teil der Anforderungen wirkt stärker system- oder cloudnah.")

    if len(missing_skills) >= 2:
        bullets.append(
            "Einige gewünschte Technologien müssten gezielt nachgeschärft werden."
        )

    return bullets[:3]


def format_skill_list(skills: list[str]) -> str:
    if len(skills) <= 1:
        return skills[0] if skills else ""
    if len(skills) == 2:
        return f"{skills[0]} und {skills[1]}"
    return f"{', '.join(skills[:-1])} und {skills[-1]}"


def contains_any(value: str, keywords: list[str]) -> bool:
    return any(keyword in value for keyword in keywords)
