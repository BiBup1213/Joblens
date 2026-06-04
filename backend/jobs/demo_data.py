from dataclasses import dataclass

from .models import ApplicationStatus, FitLevel, SourcePlatform


@dataclass(frozen=True)
class DemoJob:
    company_name: str
    job_title: str
    location: str
    work_model: str
    source_platform: str
    source_url: str
    application_status: str
    fit_level: str
    strengths: tuple[str, ...]
    missing: tuple[str, ...]
    why_it_fits: tuple[str, ...]
    what_does_not_fit: tuple[str, ...]


DEMO_JOBS = [
    DemoJob(
        company_name="Cubos GmbH",
        job_title="Software Engineer",
        location="Wolfsburg",
        work_model="Hybrid",
        source_platform=SourcePlatform.STEPSTONE,
        source_url="https://www.stepstone.de/stellenangebote/cubos-software-engineer",
        application_status=ApplicationStatus.SAVED,
        fit_level=FitLevel.GOOD,
        strengths=("Python", "REST", "Backend"),
        missing=("Go", "MQTT"),
        why_it_fits=(
            "Starke Übereinstimmung in Python, Backend und REST.",
            "Erfahrung mit verteilten Systemen ist ein Plus.",
            "Hybrid-Modell passt zu deinen Präferenzen.",
        ),
        what_does_not_fit=(
            "Go und MQTT sind nicht in deinem Profil.",
            "Erfahrung mit Cloud-Architekturen erwünscht.",
            "Kenntnisse in CI/CD werden vorausgesetzt.",
        ),
    ),
    DemoJob(
        company_name="TEQYARD",
        job_title="Python Developer",
        location="Remote",
        work_model="Remote",
        source_platform=SourcePlatform.LINKEDIN,
        source_url="https://www.linkedin.com/jobs/view/teqyard-python-developer",
        application_status=ApplicationStatus.APPLIED,
        fit_level=FitLevel.VERY_GOOD,
        strengths=("Python", "Django", "API"),
        missing=("Systemdesign", "CI/CD"),
        why_it_fits=(
            "Python und Django passen sehr gut zu deinem Profil.",
            "API-Erfahrung deckt den Kern der Rolle ab.",
            "Remote-Arbeit passt zu deinen Standortpräferenzen.",
        ),
        what_does_not_fit=(
            "Systemdesign ist noch schwächer abgedeckt.",
            "CI/CD wird explizit vorausgesetzt.",
        ),
    ),
    DemoJob(
        company_name="Rheinmetall",
        job_title="AI Consultant",
        location="Braunschweig",
        work_model="Vor Ort",
        source_platform=SourcePlatform.LINKEDIN,
        source_url="https://www.linkedin.com/jobs/view/rheinmetall-ai-consultant",
        application_status=ApplicationStatus.OPEN,
        fit_level=FitLevel.PARTIAL,
        strengths=("Python", "ML", "Data Analysis"),
        missing=("Energy Domain", "Optimierung"),
        why_it_fits=(
            "Python, ML und Analyseerfahrung sind relevant.",
            "Consulting-Anteil kann auf deine Projekterfahrung einzahlen.",
        ),
        what_does_not_fit=(
            "Branchenerfahrung ist nicht klar im Profil sichtbar.",
            "Optimierungswissen wird stärker gewichtet.",
        ),
    ),
    DemoJob(
        company_name="msg systems",
        job_title="Backend Developer",
        location="München",
        work_model="Hybrid",
        source_platform=SourcePlatform.STEPSTONE,
        source_url="https://www.stepstone.de/stellenangebote/msg-backend-developer",
        application_status=ApplicationStatus.SAVED,
        fit_level=FitLevel.NOT_SO_GOOD,
        strengths=("Java", "Spring", "SQL"),
        missing=("Kubernetes", "Cloud"),
        why_it_fits=(
            "Backend-Erfahrung ist grundsätzlich passend.",
            "SQL-Kenntnisse sind für die Rolle hilfreich.",
        ),
        what_does_not_fit=(
            "Java und Spring sind nicht deine stärksten Schwerpunkte.",
            "Kubernetes und Cloud-Erfahrung fehlen im Profil.",
        ),
    ),
    DemoJob(
        company_name="ZEISS Digital Innovation",
        job_title="Data Scientist",
        location="Jena",
        work_model="Hybrid",
        source_platform=SourcePlatform.ARBEITSAGENTUR,
        source_url="https://www.arbeitsagentur.de/jobsuche/jobangebot/zeiss-data-scientist",
        application_status=ApplicationStatus.APPLIED,
        fit_level=FitLevel.EXCELLENT,
        strengths=("Python", "SQL", "Machine Learning"),
        missing=("Deep Learning", "Computer Vision"),
        why_it_fits=(
            "Python, SQL und Machine Learning decken den Kern ab.",
            "Hybrid-Modell und Standort sind realistisch.",
            "Die Rolle passt sehr gut zu datengetriebenen Projekten.",
        ),
        what_does_not_fit=(
            "Deep Learning ist noch ausbaufähig.",
            "Computer Vision sollte gezielt belegt werden.",
        ),
    ),
]
