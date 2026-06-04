from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from jobs.services.source_platform import detect_source_platform


logger = logging.getLogger(__name__)

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
}
REQUEST_TIMEOUT_SECONDS = 10
MAX_EXTRACTED_TEXT_LENGTH = 50_000
MIN_USEFUL_CHARS = 300
MIN_USEFUL_WORDS = 40

NOISY_TAGS = [
    "script",
    "style",
    "noscript",
    "svg",
    "header",
    "footer",
    "nav",
    "aside",
    "form",
    "button",
]


@dataclass(frozen=True)
class LinkMetadata:
    company_name: str = ""
    job_title: str = ""
    location: str = ""
    work_model: str = ""
    description: str = ""
    meta_text: str = ""

    def has_structured_signal(self) -> bool:
        return bool(self.company_name or self.job_title or self.location)


@dataclass(frozen=True)
class LinkFetchResult:
    source_platform: str
    extracted_text: str
    metadata: LinkMetadata = field(default_factory=LinkMetadata)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    error: str = ""

    @property
    def has_useful_text(self) -> bool:
        return bool(self.extracted_text)


def fetch_job_text_from_url(url: str) -> LinkFetchResult:
    source_platform = detect_source_platform(url)
    diagnostics: dict[str, Any] = {
        "url": url,
        "status_code": None,
        "content_type": "",
        "html_length": 0,
        "structured_data_found": False,
        "json_ld_jobposting_found": False,
        "visible_text_length": 0,
        "meta_text_found": False,
        "fallback_reason": "",
    }

    try:
        response = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        diagnostics["status_code"] = response.status_code
        diagnostics["content_type"] = response.headers.get("content-type", "")
        diagnostics["html_length"] = len(response.text)

        if response.status_code != 200:
            diagnostics["fallback_reason"] = f"http_status_{response.status_code}"
            return fallback_result(source_platform, diagnostics)

        html = response.text
        json_ld_metadata, structured_data_found = extract_json_ld_jobposting(html)
        diagnostics["structured_data_found"] = structured_data_found
        diagnostics["json_ld_jobposting_found"] = json_ld_metadata.has_structured_signal()

        meta_metadata = extract_meta_headline_data(html)
        diagnostics["meta_text_found"] = bool(meta_metadata.meta_text)

        visible_text = extract_visible_text(html)
        diagnostics["visible_text_length"] = len(visible_text)

        metadata = merge_metadata(json_ld_metadata, meta_metadata)
        best_text = build_best_import_text(metadata, visible_text)

        if not is_useful_import_payload(best_text, metadata, visible_text):
            diagnostics["fallback_reason"] = "no_useful_text_or_structured_data"
            return fallback_result(source_platform, diagnostics)

        diagnostics["fallback_reason"] = ""
        logger.info("JobLens link import diagnostics: %s", diagnostics)
        return LinkFetchResult(
            source_platform=source_platform,
            extracted_text=best_text[:MAX_EXTRACTED_TEXT_LENGTH],
            metadata=metadata,
            diagnostics=diagnostics,
            error="",
        )
    except Exception as exc:
        diagnostics["fallback_reason"] = exc.__class__.__name__
        return fallback_result(source_platform, diagnostics, str(exc))


def fallback_result(
    source_platform: str,
    diagnostics: dict[str, Any],
    error: str = "",
) -> LinkFetchResult:
    logger.warning("JobLens link import fallback diagnostics: %s", diagnostics)
    return LinkFetchResult(
        source_platform=source_platform,
        extracted_text="",
        metadata=LinkMetadata(),
        diagnostics=diagnostics,
        error=error or diagnostics.get("fallback_reason", ""),
    )


def extract_json_ld_jobposting(html: str) -> tuple[LinkMetadata, bool]:
    soup = BeautifulSoup(html, "html.parser")
    structured_data_found = False

    for script in soup.find_all("script", attrs={"type": re.compile("ld\\+json", re.I)}):
        raw_json = script.string or script.get_text()
        if not raw_json.strip():
            continue

        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            continue

        structured_data_found = True
        for item in iter_json_objects(data):
            if is_job_posting(item):
                return metadata_from_jobposting(item), structured_data_found

    return LinkMetadata(), structured_data_found


def iter_json_objects(value: Any):
    if isinstance(value, list):
        for item in value:
            yield from iter_json_objects(item)
    elif isinstance(value, dict):
        yield value
        graph = value.get("@graph")
        if graph:
            yield from iter_json_objects(graph)
        for item in value.values():
            if isinstance(item, (dict, list)):
                yield from iter_json_objects(item)


def is_job_posting(value: dict[str, Any]) -> bool:
    item_type = value.get("@type")
    if isinstance(item_type, str):
        return "jobposting" in item_type.lower()
    if isinstance(item_type, list):
        return any(isinstance(item, str) and "jobposting" in item.lower() for item in item_type)
    return False


def metadata_from_jobposting(jobposting: dict[str, Any]) -> LinkMetadata:
    description = clean_html_text(string_value(jobposting.get("description")))
    location = extract_job_location(jobposting.get("jobLocation"))
    work_model = extract_work_model(jobposting)
    company_name = extract_hiring_organization(jobposting.get("hiringOrganization"))
    employment_type = string_value(jobposting.get("employmentType"))
    date_posted = string_value(jobposting.get("datePosted"))
    valid_through = string_value(jobposting.get("validThrough"))

    return LinkMetadata(
        company_name=company_name,
        job_title=string_value(jobposting.get("title")),
        location=location,
        work_model=work_model,
        description=description,
        meta_text="\n".join(
            item
            for item in [
                string_value(jobposting.get("title")),
                company_name,
                location,
                work_model,
                employment_type,
                date_posted,
                valid_through,
                description,
            ]
            if item
        ),
    )


def extract_hiring_organization(value: Any) -> str:
    if isinstance(value, list):
        for item in value:
            company = extract_hiring_organization(item)
            if company:
                return company
    if isinstance(value, dict):
        return string_value(value.get("name"))
    return string_value(value)


def extract_job_location(value: Any) -> str:
    if isinstance(value, list):
        for item in value:
            location = extract_job_location(item)
            if location:
                return location
    if not isinstance(value, dict):
        return ""

    address = value.get("address")
    if isinstance(address, dict):
        return ", ".join(
            item
            for item in [
                string_value(address.get("addressLocality")),
                string_value(address.get("addressRegion")),
                string_value(address.get("addressCountry")),
            ]
            if item
        )
    return string_value(value.get("name"))


def extract_work_model(jobposting: dict[str, Any]) -> str:
    location_type = string_value(jobposting.get("jobLocationType")).lower()
    if "telecommute" in location_type or "remote" in location_type:
        return "Remote"

    employment_type = string_value(jobposting.get("employmentType"))
    if employment_type:
        return ""

    return ""


def extract_meta_headline_data(html: str) -> LinkMetadata:
    soup = BeautifulSoup(html, "html.parser")
    title = first_non_empty(
        meta_content(soup, 'meta[property="og:title"]'),
        tag_text(soup.find("h1")),
        tag_text(soup.find("title")),
    )
    description = first_non_empty(
        meta_content(soup, 'meta[property="og:description"]'),
        meta_content(soup, 'meta[name="description"]'),
    )

    meta_text = "\n".join(item for item in [title, description] if item)
    company_name = extract_company_from_title(title)

    return LinkMetadata(
        company_name=company_name,
        job_title=title,
        description=description,
        meta_text=meta_text,
    )


def meta_content(soup: BeautifulSoup, selector: str) -> str:
    element = soup.select_one(selector)
    if element is None:
        return ""
    return normalize_text(element.get("content", ""))


def tag_text(element: Any) -> str:
    if element is None:
        return ""
    return normalize_text(element.get_text(" "))


def extract_company_from_title(title: str) -> str:
    if not title:
        return ""
    parts = re.split(r"\s[-–|]\s", title)
    for part in reversed(parts):
        if re.search(r"\b(GmbH & Co\. KG|GmbH|AG|SE|UG)\b", part):
            return normalize_text(part)
    return ""


def extract_visible_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for element in soup(NOISY_TAGS):
        element.decompose()

    raw_text = soup.get_text(separator="\n")
    lines = []

    for line in raw_text.splitlines():
        normalized = normalize_text(line)
        if len(normalized) < 3:
            continue
        if is_cookie_noise(normalized):
            continue
        lines.append(normalized)

    return "\n".join(lines)[:MAX_EXTRACTED_TEXT_LENGTH]


def is_useful_import_payload(
    best_text: str,
    metadata: LinkMetadata,
    visible_text: str,
) -> bool:
    if is_useful_text(visible_text):
        return True

    if metadata.has_structured_signal() and len(best_text) >= 120:
        return True

    if metadata.description and len(metadata.description) >= 180:
        return True

    return False


def is_useful_text(text: str) -> bool:
    if len(text) < MIN_USEFUL_CHARS:
        return False

    words = re.findall(r"\b[\wÄÖÜäöüß-]{3,}\b", text)
    if len(words) < MIN_USEFUL_WORDS:
        return False

    lowered_text = text.lower()
    noisy_terms = ["cookie", "datenschutz", "navigation", "login", "registrieren"]
    noisy_hits = sum(term in lowered_text for term in noisy_terms)
    job_terms = [
        "developer",
        "engineer",
        "entwickler",
        "consultant",
        "python",
        "aufgaben",
        "profil",
        "stellenanzeige",
        "qualifikation",
    ]

    if noisy_hits >= 3 and not any(term in lowered_text for term in job_terms):
        return False

    return True


def build_best_import_text(metadata: LinkMetadata, visible_text: str) -> str:
    parts = [
        metadata.job_title,
        metadata.company_name,
        metadata.location,
        metadata.work_model,
        metadata.description,
        metadata.meta_text,
        visible_text if is_useful_text(visible_text) else "",
    ]
    return "\n".join(dedupe_non_empty(parts))[:MAX_EXTRACTED_TEXT_LENGTH]


def merge_metadata(primary: LinkMetadata, secondary: LinkMetadata) -> LinkMetadata:
    return LinkMetadata(
        company_name=primary.company_name or secondary.company_name,
        job_title=primary.job_title or secondary.job_title,
        location=primary.location or secondary.location,
        work_model=primary.work_model or secondary.work_model,
        description=primary.description or secondary.description,
        meta_text="\n".join(
            dedupe_non_empty([primary.meta_text, secondary.meta_text])
        ),
    )


def clean_html_text(value: str) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return normalize_text(soup.get_text(" "))


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def string_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return normalize_text(value)
    return normalize_text(str(value))


def first_non_empty(*values: str) -> str:
    for value in values:
        if value:
            return value
    return ""


def dedupe_non_empty(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        normalized = normalize_text(value)
        if not normalized or normalized.lower() in seen:
            continue
        seen.add(normalized.lower())
        result.append(normalized)
    return result


def is_cookie_noise(value: str) -> bool:
    lowered = value.lower()
    noise_terms = ["cookie", "datenschutz", "einwilligung", "akzeptieren"]
    return len(value) < 80 and sum(term in lowered for term in noise_terms) >= 2

