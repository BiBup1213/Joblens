from django.contrib import admin

from .models import JobAnalysis, JobPosting, JobSkill


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 0


class JobAnalysisInline(admin.StackedInline):
    model = JobAnalysis
    extra = 0
    max_num = 1


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "job_title",
        "location",
        "work_model",
        "source_platform",
        "application_status",
        "fit_level",
        "created_at",
    )
    list_filter = (
        "application_status",
        "fit_level",
        "source_platform",
        "work_model",
    )
    search_fields = ("company_name", "job_title", "location", "raw_text")
    inlines = [JobSkillInline, JobAnalysisInline]


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "job", "created_at")
    list_filter = ("kind",)
    search_fields = ("name", "job__company_name", "job__job_title")


@admin.register(JobAnalysis)
class JobAnalysisAdmin(admin.ModelAdmin):
    list_display = ("job", "updated_at")
    search_fields = ("job__company_name", "job__job_title")
