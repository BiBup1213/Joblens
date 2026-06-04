from django.db import models


class ProfileSkillLevel(models.TextChoices):
    BEGINNER = "beginner", "Anfänger"
    INTERMEDIATE = "intermediate", "Mittel"
    STRONG = "strong", "Stark"
    EXPERT = "expert", "Experte"


class UserProfile(models.Model):
    display_name = models.CharField(max_length=255)
    target_roles = models.JSONField(default=list, blank=True)
    salary_expectation = models.CharField(max_length=120, blank=True)
    location_preferences = models.JSONField(default=list, blank=True)
    remote_preference = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_name"]

    def __str__(self) -> str:
        return self.display_name


class ProfileSkill(models.Model):
    profile = models.ForeignKey(
        UserProfile,
        related_name="skills",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=120)
    level = models.CharField(
        max_length=32,
        choices=ProfileSkillLevel.choices,
        default=ProfileSkillLevel.INTERMEDIATE,
    )
    years_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "name"],
                name="unique_profile_skill_name",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_level_display()})"
