from rest_framework import serializers

from .models import (
    ApplicationStatus,
    JobAnalysis,
    JobPosting,
    JobSkill,
    SkillKind,
)


class JobSkillSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = JobSkill
        fields = ["id", "job", "name", "kind", "kind_label", "created_at"]
        read_only_fields = ["id", "created_at"]


class NestedJobSkillSerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = JobSkill
        fields = ["id", "name", "kind", "kind_label"]


class JobAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAnalysis
        fields = [
            "id",
            "job",
            "why_it_fits",
            "what_does_not_fit",
            "next_step_note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_why_it_fits(self, value):
        return self._validate_string_list(value, "why_it_fits")

    def validate_what_does_not_fit(self, value):
        return self._validate_string_list(value, "what_does_not_fit")

    def _validate_string_list(self, value, field_name):
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise serializers.ValidationError(f"{field_name} must be a list of strings.")
        return value


class NestedJobAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAnalysis
        fields = ["why_it_fits", "what_does_not_fit", "next_step_note"]


class JobPostingSerializer(serializers.ModelSerializer):
    application_status_label = serializers.CharField(
        source="get_application_status_display",
        read_only=True,
    )
    fit_level_label = serializers.CharField(source="get_fit_level_display", read_only=True)
    source_platform_label = serializers.CharField(
        source="get_source_platform_display",
        read_only=True,
    )
    strengths = serializers.SerializerMethodField()
    missing_skills = serializers.SerializerMethodField()
    analysis = serializers.SerializerMethodField()

    class Meta:
        model = JobPosting
        fields = [
            "id",
            "company_name",
            "job_title",
            "location",
            "work_model",
            "source_platform",
            "source_platform_label",
            "source_url",
            "raw_text",
            "application_status",
            "application_status_label",
            "fit_level",
            "fit_level_label",
            "strengths",
            "missing_skills",
            "analysis",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_strengths(self, obj):
        skills = obj.skills.filter(kind=SkillKind.STRENGTH)
        return NestedJobSkillSerializer(skills, many=True).data

    def get_missing_skills(self, obj):
        skills = obj.skills.filter(kind=SkillKind.MISSING)
        return NestedJobSkillSerializer(skills, many=True).data

    def get_analysis(self, obj):
        try:
            analysis = obj.analysis
        except JobAnalysis.DoesNotExist:
            return {
                "why_it_fits": [],
                "what_does_not_fit": [],
                "next_step_note": "",
            }
        return NestedJobAnalysisSerializer(analysis).data

    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Company name must not be empty.")
        return value.strip()

    def validate_job_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Job title must not be empty.")
        return value.strip()


class ChangeStatusSerializer(serializers.Serializer):
    application_status = serializers.ChoiceField(
        choices=ApplicationStatus.choices,
        error_messages={
            "invalid_choice": "Unsupported application status.",
            "required": "application_status is required.",
        },
    )
