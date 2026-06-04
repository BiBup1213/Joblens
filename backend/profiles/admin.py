from django.contrib import admin

from .models import ProfileSkill, UserProfile


class ProfileSkillInline(admin.TabularInline):
    model = ProfileSkill
    extra = 0


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "display_name",
        "salary_expectation",
        "remote_preference",
        "created_at",
        "updated_at",
    )
    search_fields = ("display_name",)
    inlines = [ProfileSkillInline]


@admin.register(ProfileSkill)
class ProfileSkillAdmin(admin.ModelAdmin):
    list_display = ("name", "profile", "level", "years_experience", "created_at")
    list_filter = ("level",)
    search_fields = ("name", "profile__display_name")
