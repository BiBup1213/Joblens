from django.db import models


class DocumentType(models.TextChoices):
    CV = "cv", "Lebenslauf"
    WORK_REFERENCE = "work_reference", "Arbeitszeugnis"
    COVER_LETTER = "cover_letter", "Anschreiben"
    PROJECT_DESCRIPTION = "project_description", "Projektbeschreibung"
    CERTIFICATE = "certificate", "Zertifikat"
    OTHER = "other", "Sonstiges"


class DocumentAnalysisStatus(models.TextChoices):
    PENDING = "pending", "Ausstehend"
    EXTRACTED = "extracted", "Extrahiert"
    FAILED = "failed", "Fehlgeschlagen"


class ProfileDocument(models.Model):
    title = models.CharField(max_length=255)
    document_type = models.CharField(
        max_length=40,
        choices=DocumentType.choices,
        default=DocumentType.OTHER,
    )
    file = models.FileField(upload_to="profile_documents/", blank=True)
    extracted_text = models.TextField(blank=True)
    analysis_status = models.CharField(
        max_length=32,
        choices=DocumentAnalysisStatus.choices,
        default=DocumentAnalysisStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self) -> str:
        return self.title
