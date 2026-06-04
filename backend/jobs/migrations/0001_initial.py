from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="JobPosting",
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
                ("company_name", models.CharField(max_length=255)),
                ("job_title", models.CharField(max_length=255)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("work_model", models.CharField(blank=True, max_length=80)),
                (
                    "source_platform",
                    models.CharField(
                        choices=[
                            ("stepstone", "StepStone"),
                            ("linkedin", "LinkedIn"),
                            ("arbeitsagentur", "Arbeitsagentur"),
                            ("xing", "XING"),
                            ("indeed", "Indeed"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=32,
                    ),
                ),
                ("source_url", models.URLField(blank=True)),
                ("raw_text", models.TextField(blank=True)),
                (
                    "application_status",
                    models.CharField(
                        choices=[
                            ("saved", "Gespeichert"),
                            ("review", "Prüfen"),
                            ("open", "Offen"),
                            ("applied", "Beworben"),
                            ("interview", "Gespräch"),
                            ("rejected", "Absage"),
                            ("archived", "Archiviert"),
                        ],
                        default="saved",
                        max_length=32,
                    ),
                ),
                (
                    "fit_level",
                    models.CharField(
                        choices=[
                            ("not_so_good", "Passt nicht so gut"),
                            ("partial", "Passt teilweise"),
                            ("good", "Passt gut"),
                            ("very_good", "Passt sehr gut"),
                            ("excellent", "Passt hervorragend"),
                        ],
                        default="partial",
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
        migrations.CreateModel(
            name="JobAnalysis",
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
                ("why_it_fits", models.JSONField(blank=True, default=list)),
                ("what_does_not_fit", models.JSONField(blank=True, default=list)),
                ("next_step_note", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "job",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="analysis",
                        to="jobs.jobposting",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "job analyses",
            },
        ),
        migrations.CreateModel(
            name="JobSkill",
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
                ("name", models.CharField(max_length=120)),
                (
                    "kind",
                    models.CharField(
                        choices=[("strength", "Stärke"), ("missing", "Fehlt")],
                        max_length=24,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skills",
                        to="jobs.jobposting",
                    ),
                ),
            ],
            options={
                "ordering": ["id"],
            },
        ),
        migrations.AddConstraint(
            model_name="jobskill",
            constraint=models.UniqueConstraint(
                fields=("job", "name", "kind"),
                name="unique_job_skill_kind",
            ),
        ),
    ]
