from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch

from jobs.models import (
    ApplicationStatus,
    FitLevel,
    JobAnalysis,
    JobPosting,
    JobSkill,
    SkillKind,
    SourcePlatform,
)
from jobs.services.source_platform import detect_source_platform


class MockHttpResponse:
    def __init__(
        self,
        text: str,
        status_code: int = 200,
        content_type: str = "text/html; charset=utf-8",
    ):
        self.text = text
        self.status_code = status_code
        self.headers = {"content-type": content_type}


class LinkImporterServiceTests(TestCase):
    def test_detect_source_platform_from_known_domains(self):
        cases = {
            "https://www.stepstone.de/stellenangebote/example": SourcePlatform.STEPSTONE,
            "https://www.linkedin.com/jobs/view/example": SourcePlatform.LINKEDIN,
            "https://www.arbeitsagentur.de/jobsuche/jobangebot/example": SourcePlatform.ARBEITSAGENTUR,
            "https://www.xing.com/jobs/example": SourcePlatform.XING,
            "https://de.indeed.com/viewjob?jk=example": SourcePlatform.INDEED,
            "https://jobs.example.com/posting": SourcePlatform.OTHER,
        }

        for url, source_platform in cases.items():
            with self.subTest(url=url):
                self.assertEqual(detect_source_platform(url), source_platform)


class JobPostingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.job = JobPosting.objects.create(
            company_name="Cubos GmbH",
            job_title="Software Engineer",
            location="Wolfsburg",
            work_model="Hybrid",
            source_platform=SourcePlatform.STEPSTONE,
            application_status=ApplicationStatus.SAVED,
            fit_level=FitLevel.GOOD,
        )
        JobSkill.objects.create(
            job=self.job,
            name="Python",
            kind=SkillKind.STRENGTH,
        )
        JobSkill.objects.create(
            job=self.job,
            name="Go",
            kind=SkillKind.MISSING,
        )
        JobAnalysis.objects.create(
            job=self.job,
            why_it_fits=["Starke Übereinstimmung in Python."],
            what_does_not_fit=["Go ist nicht im Profil."],
        )

    def test_can_list_jobs(self):
        response = self.client.get(reverse("job-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["company_name"], "Cubos GmbH")
        self.assertEqual(response.data[0]["strengths"][0]["name"], "Python")
        self.assertEqual(response.data[0]["missing_skills"][0]["name"], "Go")
        self.assertIn("why_it_fits", response.data[0]["analysis"])

    def test_can_create_job(self):
        payload = {
            "company_name": "TEQYARD",
            "job_title": "Python Developer",
            "location": "Remote",
            "work_model": "Remote",
            "source_platform": SourcePlatform.LINKEDIN,
            "application_status": ApplicationStatus.OPEN,
            "fit_level": FitLevel.VERY_GOOD,
        }

        response = self.client.post(reverse("job-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "TEQYARD")
        self.assertEqual(JobPosting.objects.count(), 2)

    def test_can_retrieve_job_detail(self):
        response = self.client.get(reverse("job-detail", args=[self.job.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["fit_level_label"], "Passt gut")
        self.assertEqual(
            response.data["analysis"]["why_it_fits"],
            ["Starke Übereinstimmung in Python."],
        )

    def test_can_update_application_status_with_patch(self):
        response = self.client.patch(
            reverse("job-detail", args=[self.job.id]),
            {"application_status": ApplicationStatus.APPLIED},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.application_status, ApplicationStatus.APPLIED)

    def test_can_update_application_status_with_action(self):
        response = self.client.post(
            reverse("job-change-status", args=[self.job.id]),
            {"application_status": ApplicationStatus.INTERVIEW},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.job.refresh_from_db()
        self.assertEqual(self.job.application_status, ApplicationStatus.INTERVIEW)

    def test_change_status_rejects_invalid_status(self):
        response = self.client.post(
            reverse("job-change-status", args=[self.job.id]),
            {"application_status": "invalid"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.job.refresh_from_db()
        self.assertEqual(self.job.application_status, ApplicationStatus.SAVED)

    @patch("jobs.services.link_importer.requests.get")
    def test_import_link_endpoint_creates_job(self, mock_get):
        mock_get.return_value = MockHttpResponse("", status_code=500)

        response = self.client.post(
            reverse("job-import-link"),
            {"url": "https://www.stepstone.de/stellenangebote/example"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Unbekanntes Unternehmen")
        self.assertEqual(response.data["job_title"], "Importierte Stellenanzeige")
        self.assertEqual(response.data["source_platform"], SourcePlatform.STEPSTONE)
        self.assertEqual(response.data["application_status"], ApplicationStatus.SAVED)
        self.assertEqual(response.data["fit_level"], FitLevel.PARTIAL)
        self.assertEqual(response.data["strengths"], [])
        self.assertEqual(response.data["missing_skills"], [])
        self.assertIn(
            "konnte aber noch nicht automatisch ausgewertet werden",
            response.data["analysis"]["why_it_fits"][0],
        )

    @patch("jobs.services.link_importer.requests.get")
    def test_import_link_with_mocked_html_creates_structured_job(self, mock_get):
        mock_get.return_value = MockHttpResponse(successful_job_html())

        response = self.client.post(
            reverse("job-import-link"),
            {"url": "https://www.stepstone.de/stellenangebote/example"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Cubos GmbH")
        self.assertEqual(response.data["job_title"], "Software Engineer")
        self.assertEqual(response.data["location"], "Wolfsburg")
        self.assertEqual(response.data["work_model"], "Hybrid")
        self.assertEqual(response.data["source_platform"], SourcePlatform.STEPSTONE)
        self.assertIn("Software Engineer", response.data["raw_text"])
        strength_names = [skill["name"] for skill in response.data["strengths"]]
        self.assertIn("Python", strength_names)
        self.assertIn("Django", strength_names)
        self.assertIn("REST", strength_names)
        self.assertEqual(strength_names.count("Python"), 1)
        self.assertGreater(len(response.data["analysis"]["why_it_fits"]), 0)

    @patch("jobs.services.link_importer.requests.get")
    def test_import_link_with_json_ld_jobposting_creates_structured_job(self, mock_get):
        mock_get.return_value = MockHttpResponse(json_ld_jobposting_html())

        response = self.client.post(
            reverse("job-import-link"),
            {"url": "https://www.stepstone.de/stellenangebote/jsonld"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Schema Jobs GmbH")
        self.assertEqual(response.data["job_title"], "Python Developer")
        self.assertEqual(response.data["location"], "Berlin, BE, DE")
        self.assertEqual(response.data["source_platform"], SourcePlatform.STEPSTONE)
        self.assertIn("Python Developer", response.data["raw_text"])
        self.assertIn("Python", {skill["name"] for skill in response.data["strengths"]})
        self.assertNotIn("<p>", response.data["raw_text"])

    @patch("jobs.services.link_importer.requests.get")
    def test_import_link_supports_json_ld_graph(self, mock_get):
        mock_get.return_value = MockHttpResponse(json_ld_graph_jobposting_html())

        response = self.client.post(
            reverse("job-import-link"),
            {"url": "https://www.linkedin.com/jobs/view/jsonld"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Graph AG")
        self.assertEqual(response.data["job_title"], "Data Scientist")
        self.assertEqual(response.data["location"], "Jena")
        self.assertEqual(response.data["source_platform"], SourcePlatform.LINKEDIN)

    @patch("jobs.services.link_importer.requests.get")
    def test_import_link_meta_fallback_improves_placeholder_data(self, mock_get):
        mock_get.return_value = MockHttpResponse(meta_job_html())

        response = self.client.post(
            reverse("job-import-link"),
            {"url": "https://jobs.example.com/software-engineer"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Cubos GmbH")
        self.assertIn("Software Engineer", response.data["job_title"])
        self.assertEqual(response.data["source_platform"], SourcePlatform.OTHER)
        self.assertIn("Python", {skill["name"] for skill in response.data["strengths"]})

    @patch("jobs.services.link_importer.requests.get")
    def test_import_link_with_weak_html_falls_back_to_placeholder(self, mock_get):
        mock_get.return_value = MockHttpResponse(
            "<html><body><nav>Login Registrieren Cookie Datenschutz Navigation</nav><main>OK</main></body></html>"
        )

        response = self.client.post(
            reverse("job-import-link"),
            {"url": "https://www.linkedin.com/jobs/view/example"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Unbekanntes Unternehmen")
        self.assertEqual(response.data["job_title"], "Importierte Stellenanzeige")
        self.assertEqual(response.data["source_platform"], SourcePlatform.LINKEDIN)
        self.assertEqual(response.data["raw_text"], "")
        self.assertIn(
            "nicht zuverlässig ausgelesen",
            response.data["analysis"]["what_does_not_fit"][0],
        )

    def test_import_link_rejects_invalid_url(self):
        response = self.client.post(
            reverse("job-import-link"),
            {"url": "not-a-url"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_text_creates_placeholder_job(self):
        response = self.client.post(
            reverse("job-import-text"),
            {"text": "Python backend developer role"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["raw_text"], "Python backend developer role")
        self.assertEqual(response.data["source_platform"], SourcePlatform.OTHER)

    def test_import_text_rejects_empty_text(self):
        response = self.client.post(
            reverse("job-import-text"),
            {"text": ""},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_text_extracts_useful_structured_data(self):
        response = self.client.post(
            reverse("job-import-text"),
            {
                "text": "\n".join(
                    [
                        "Software Engineer",
                        "Cubos GmbH",
                        "Standort Wolfsburg, Hybrid",
                        "Wir suchen Erfahrung mit Python, REST und Django.",
                    ]
                )
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Cubos GmbH")
        self.assertEqual(response.data["job_title"], "Software Engineer")
        self.assertEqual(response.data["location"], "Wolfsburg")
        self.assertEqual(response.data["work_model"], "Hybrid")
        self.assertIn(response.data["fit_level"], [FitLevel.GOOD, FitLevel.VERY_GOOD])
        strength_names = {skill["name"] for skill in response.data["strengths"]}
        self.assertSetEqual(strength_names, {"Python", "Django", "REST"})
        self.assertGreater(len(response.data["analysis"]["why_it_fits"]), 0)

    def test_import_text_detects_missing_skills(self):
        response = self.client.post(
            reverse("job-import-text"),
            {
                "text": "Backend Developer mit Go, MQTT und Kubernetes Erfahrung gesucht."
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        missing_names = {skill["name"] for skill in response.data["missing_skills"]}
        self.assertSetEqual(missing_names, {"Go", "MQTT", "Kubernetes"})
        self.assertEqual(response.data["fit_level"], FitLevel.NOT_SO_GOOD)
        self.assertGreater(len(response.data["analysis"]["what_does_not_fit"]), 0)

    def test_import_text_keeps_safe_fallback_for_unstructured_text(self):
        response = self.client.post(
            reverse("job-import-text"),
            {"text": "Wir suchen Unterstützung für spannende Aufgaben."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["company_name"], "Unbekanntes Unternehmen")
        self.assertEqual(response.data["job_title"], "Importierte Stellenanzeige")
        self.assertEqual(response.data["fit_level"], FitLevel.PARTIAL)
        self.assertEqual(response.data["strengths"], [])
        self.assertEqual(response.data["missing_skills"], [])
        self.assertIn(
            "zu wenig strukturierte Informationen",
            response.data["analysis"]["why_it_fits"][0],
        )

    def test_import_text_does_not_create_duplicate_skills(self):
        response = self.client.post(
            reverse("job-import-text"),
            {"text": "Python python PYTHON Django Django REST REST"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        skill_names = [skill["name"] for skill in response.data["strengths"]]
        self.assertEqual(skill_names.count("Python"), 1)
        self.assertEqual(skill_names.count("Django"), 1)
        self.assertEqual(skill_names.count("REST"), 1)

    @patch("jobs.services.link_importer.requests.get")
    def test_import_bulk_returns_partial_results_and_errors(self, mock_get):
        mock_get.return_value = MockHttpResponse("", status_code=500)

        response = self.client.post(
            reverse("job-import-bulk"),
            {
                "urls": [
                    "https://www.linkedin.com/jobs/view/example",
                    "not-a-url",
                ]
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(len(response.data["errors"]), 1)
        self.assertEqual(
            response.data["results"][0]["source_platform"],
            SourcePlatform.LINKEDIN,
        )


class SeedDemoDataCommandTests(TestCase):
    def test_seed_demo_data_creates_expected_jobs(self):
        call_command("seed_demo_data")

        self.assertEqual(JobPosting.objects.count(), 5)
        self.assertTrue(
            JobPosting.objects.filter(company_name="ZEISS Digital Innovation").exists()
        )
        self.assertEqual(JobSkill.objects.count(), 25)
        self.assertEqual(JobAnalysis.objects.count(), 5)


def successful_job_html() -> str:
    body = """
    <html>
      <head><title>Job</title><script>ignored()</script></head>
      <body>
        <header>Navigation Login Cookie Datenschutz</header>
        <main>
          <h1>Software Engineer</h1>
          <p>Cubos GmbH</p>
          <p>Standort Wolfsburg, Hybrid</p>
          <p>
            Wir suchen eine Person fuer Backend Entwicklung mit Python, Python,
            Django und REST API Erfahrung. Du arbeitest an Schnittstellen,
            Datenmodellen, Services und sauberer Dokumentation.
          </p>
          <p>
            Aufgaben sind Entwicklung, Testing, Deployment, Zusammenarbeit im
            Produktteam, Analyse von Anforderungen, Code Reviews, Git Workflows
            und Docker basierte lokale Entwicklungsumgebungen.
          </p>
          <p>
            Deine Erfahrung mit SQL, PostgreSQL und Machine Learning ist ein Plus.
            Das Team arbeitet hybrid in Wolfsburg und kommuniziert eng mit
            Stakeholdern aus Produkt, Backend und Plattform.
          </p>
        </main>
        <footer>Impressum Datenschutz</footer>
      </body>
    </html>
    """
    return body


def json_ld_jobposting_html() -> str:
    return """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "JobPosting",
          "title": "Python Developer",
          "hiringOrganization": {"@type": "Organization", "name": "Schema Jobs GmbH"},
          "jobLocation": {
            "@type": "Place",
            "address": {
              "@type": "PostalAddress",
              "addressLocality": "Berlin",
              "addressRegion": "BE",
              "addressCountry": "DE"
            }
          },
          "description": "<p>Wir suchen Python, Django und REST Erfahrung fuer API Entwicklung, Testing, SQL Datenmodelle, Git Workflows, Docker Umgebungen und Backend Services. Die Rolle arbeitet eng mit Produktteams zusammen und umfasst Analyse, Implementierung und technische Dokumentation.</p>"
        }
        </script>
      </head>
      <body><main>Cookie Hinweis</main></body>
    </html>
    """


def json_ld_graph_jobposting_html() -> str:
    return """
    <html>
      <head>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@graph": [
            {"@type": "Organization", "name": "Graph AG"},
            {
              "@type": ["Thing", "JobPosting"],
              "title": "Data Scientist",
              "hiringOrganization": {"name": "Graph AG"},
              "jobLocation": {"address": {"addressLocality": "Jena"}},
              "description": "Data Scientist Rolle mit Python, SQL, Machine Learning und Data Analysis. Aufgaben umfassen Modellierung, Analyse, Reporting, Experimente, Abstimmung mit Fachbereichen und Dokumentation von Ergebnissen in einem hybriden Team."
            }
          ]
        }
        </script>
      </head>
      <body></body>
    </html>
    """


def meta_job_html() -> str:
    return """
    <html>
      <head>
        <title>Software Engineer (m/w/d) Energy Systems - Cubos GmbH</title>
        <meta property="og:title" content="Software Engineer (m/w/d) Energy Systems - Cubos GmbH" />
        <meta name="description" content="Backend Entwicklung mit Python, REST, Django, SQL, Docker, Git und API Design. Die Position arbeitet hybrid in Wolfsburg und umfasst Analyse, Implementierung, Tests, Dokumentation und Zusammenarbeit mit Produktteams." />
      </head>
      <body><main>Mehr erfahren</main></body>
    </html>
    """
