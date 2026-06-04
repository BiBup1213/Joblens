from urllib.parse import urlparse

from jobs.models import SourcePlatform


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
