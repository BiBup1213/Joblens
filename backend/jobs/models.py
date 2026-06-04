from django.core.exceptions import ValidationError
from django.db import models


class ApplicationStatus(models.TextChoices):
    SAVED = "saved", "Gespeichert"
    REVIEW = "review", "Prüfen"
    OPEN = "open", "Offen"
    APPLIED = "applied", "Beworben"
    INTERVIEW = "interview", "Gespräch"
    REJECTED = "rejected", "Absage"
    ARCHIVED = "archived", "Archiviert"


class FitLevel(models.TextChoices):
    NOT_SO_GOOD = "not_so_good", "Passt nicht so gut"
    PARTIAL = "partial", "Passt teilweise"
    GOOD = "good", "Passt gut"
    VERY_GOOD = "very_good", "Passt sehr gut"
    EXCELLENT = "excellent", "Passt hervorragend"


class SourcePlatform(models.TextChoices):
    STEPSTONE = "stepstone", "StepStone"
    LINKEDIN = "linkedin", "LinkedIn"
    ARBEITSAGENTUR = "arbeitsagentur", "Arbeitsagentur"
    XING = "xing", "XING"
    INDEED = "indeed", "Indeed"
    OTHER = "other", "Other"


class SkillKind(models.TextChoices):
    STRENGTH = "strength", "Stärke"
    MISSING = "missing", "Fehlt"


class JobPosting(models.Model):
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    work_model = models.CharField(max_length=80, blank=True)
    source_platform = models.CharField(
        max_length=32,
        choices=SourcePlatform.choices,
        default=SourcePlatform.OTHER,
    )
    source_url = models.URLField(blank=True)
    raw_text = models.TextField(blank=True)
    application_status = models.CharField(
        max_length=32,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.SAVED,
    )
    fit_level = models.CharField(
        max_length=32,
        choices=FitLevel.choices,
        default=FitLevel.PARTIAL,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return f"{self.company_name} - {self.job_title}"

    def clean(self) -> None:
        if not self.company_name.strip():
            raise ValidationError({"company_name": "Company name must not be empty."})
        if not self.job_title.strip():
            raise ValidationError({"job_title": "Job title must not be empty."})


class JobSkill(models.Model):
    job = models.ForeignKey(
        JobPosting,
        related_name="skills",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=24, choices=SkillKind.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["job", "name", "kind"],
                name="unique_job_skill_kind",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_kind_display()})"


class JobAnalysis(models.Model):
    job = models.OneToOneField(
        JobPosting,
        related_name="analysis",
        on_delete=models.CASCADE,
    )
    why_it_fits = models.JSONField(default=list, blank=True)
    what_does_not_fit = models.JSONField(default=list, blank=True)
    next_step_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "job analyses"

    def __str__(self) -> str:
        return f"Analysis for {self.job}"
