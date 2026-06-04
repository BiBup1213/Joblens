from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from jobs.models import (
    ApplicationStatus,
    FitLevel,
    JobAnalysis,
    JobPosting,
    JobSkill,
    SkillKind,
    SourcePlatform,
)


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

    def test_import_link_endpoint_creates_job(self):
        response = self.client.post(
            reverse("job-import-link"),
            {"url": "https://www.stepstone.de/stellenangebote/example"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["source_platform"], SourcePlatform.STEPSTONE)
        self.assertGreater(len(response.data["strengths"]), 0)
        self.assertIsNotNone(response.data["analysis"])


class SeedDemoDataCommandTests(TestCase):
    def test_seed_demo_data_creates_expected_jobs(self):
        call_command("seed_demo_data")

        self.assertEqual(JobPosting.objects.count(), 5)
        self.assertTrue(
            JobPosting.objects.filter(company_name="ZEISS Digital Innovation").exists()
        )
        self.assertEqual(JobSkill.objects.count(), 25)
        self.assertEqual(JobAnalysis.objects.count(), 5)
