from django.contrib import admin

from .models import ProfileDocument


@admin.register(ProfileDocument)
class ProfileDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "document_type",
        "analysis_status",
        "created_at",
        "updated_at",
    )
    list_filter = ("document_type", "analysis_status")
    search_fields = ("title", "extracted_text")
