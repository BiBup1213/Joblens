from django.core.management.base import BaseCommand

from jobs.demo_data import DEMO_JOBS
from jobs.models import JobAnalysis, JobPosting, JobSkill, SkillKind


class Command(BaseCommand):
    help = "Create the demo job postings used by the JobLens dashboard."

    def handle(self, *args, **options):
        created_count = 0

        for demo in DEMO_JOBS:
            job, created = JobPosting.objects.update_or_create(
                company_name=demo.company_name,
                job_title=demo.job_title,
                defaults={
                    "location": demo.location,
                    "work_model": demo.work_model,
                    "source_platform": demo.source_platform,
                    "source_url": demo.source_url,
                    "application_status": demo.application_status,
                    "fit_level": demo.fit_level,
                },
            )
            created_count += int(created)

            job.skills.all().delete()
            JobSkill.objects.bulk_create(
                [
                    JobSkill(job=job, name=name, kind=SkillKind.STRENGTH)
                    for name in demo.strengths
                ]
                + [
                    JobSkill(job=job, name=name, kind=SkillKind.MISSING)
                    for name in demo.missing
                ]
            )

            JobAnalysis.objects.update_or_create(
                job=job,
                defaults={
                    "why_it_fits": list(demo.why_it_fits),
                    "what_does_not_fit": list(demo.what_does_not_fit),
                    "next_step_note": "",
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(DEMO_JOBS)} demo jobs ({created_count} created)."
            )
        )
