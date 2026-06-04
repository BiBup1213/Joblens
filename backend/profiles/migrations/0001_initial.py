from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserProfile",
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
                ("display_name", models.CharField(max_length=255)),
                ("target_roles", models.JSONField(blank=True, default=list)),
                ("salary_expectation", models.CharField(blank=True, max_length=120)),
                ("location_preferences", models.JSONField(blank=True, default=list)),
                ("remote_preference", models.CharField(blank=True, max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["display_name"],
            },
        ),
        migrations.CreateModel(
            name="ProfileSkill",
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
                    "level",
                    models.CharField(
                        choices=[
                            ("beginner", "Anfänger"),
                            ("intermediate", "Mittel"),
                            ("strong", "Stark"),
                            ("expert", "Experte"),
                        ],
                        default="intermediate",
                        max_length=32,
                    ),
                ),
                (
                    "years_experience",
                    models.DecimalField(
                        blank=True,
                        decimal_places=1,
                        max_digits=4,
                        null=True,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="skills",
                        to="profiles.userprofile",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.AddConstraint(
            model_name="profileskill",
            constraint=models.UniqueConstraint(
                fields=("profile", "name"),
                name="unique_profile_skill_name",
            ),
        ),
    ]
