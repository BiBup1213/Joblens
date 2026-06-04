from rest_framework import serializers

from .models import ProfileDocument


class ProfileDocumentSerializer(serializers.ModelSerializer):
    document_type_label = serializers.CharField(
        source="get_document_type_display",
        read_only=True,
    )
    analysis_status_label = serializers.CharField(
        source="get_analysis_status_display",
        read_only=True,
    )

    class Meta:
        model = ProfileDocument
        fields = [
            "id",
            "title",
            "document_type",
            "document_type_label",
            "file",
            "extracted_text",
            "analysis_status",
            "analysis_status_label",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
