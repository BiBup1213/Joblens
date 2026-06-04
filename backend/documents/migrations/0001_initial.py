from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ProfileDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "document_type",
                    models.CharField(
                        choices=[
                            ("cv", "Lebenslauf"),
                            ("work_reference", "Arbeitszeugnis"),
                            ("cover_letter", "Anschreiben"),
                            ("project_description", "Projektbeschreibung"),
                            ("certificate", "Zertifikat"),
                            ("other", "Sonstiges"),
                        ],
                        default="other",
                        max_length=40,
                    ),
                ),
                (
                    "file",
                    models.FileField(blank=True, upload_to="profile_documents/"),
                ),
                ("extracted_text", models.TextField(blank=True)),
                (
                    "analysis_status",
                    models.CharField(
                        choices=[
                            ("pending", "Ausstehend"),
                            ("extracted", "Extrahiert"),
                            ("failed", "Fehlgeschlagen"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at", "-id"],
            },
        ),
    ]
