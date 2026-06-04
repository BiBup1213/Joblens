from rest_framework import serializers

from .models import ProfileSkill, UserProfile


class ProfileSkillSerializer(serializers.ModelSerializer):
    level_label = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = ProfileSkill
        fields = [
            "id",
            "profile",
            "name",
            "level",
            "level_label",
            "years_experience",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class NestedProfileSkillSerializer(serializers.ModelSerializer):
    level_label = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = ProfileSkill
        fields = ["id", "name", "level", "level_label", "years_experience"]


class UserProfileSerializer(serializers.ModelSerializer):
    skills = NestedProfileSkillSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "display_name",
            "target_roles",
            "salary_expectation",
            "location_preferences",
            "remote_preference",
            "skills",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
