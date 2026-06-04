from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.serializers import CharField, ListField, Serializer, URLField

from .models import JobAnalysis, JobPosting, JobSkill
from .serializers import (
    ChangeStatusSerializer,
    JobAnalysisSerializer,
    JobPostingSerializer,
    JobSkillSerializer,
)
from .services.importer import (
    import_job_from_link,
    import_job_from_text,
)


class ImportLinkSerializer(Serializer):
    url = URLField(error_messages={"required": "url is required."})


class ImportTextSerializer(Serializer):
    text = CharField(allow_blank=False, trim_whitespace=True)


class ImportBulkSerializer(Serializer):
    urls = ListField(child=CharField(trim_whitespace=True), allow_empty=False)

    def validate_urls(self, value):
        urls = [url for url in value if url]
        if not urls:
            raise ValidationError("At least one URL is required.")
        return urls


class JobPostingViewSet(viewsets.ModelViewSet):
    serializer_class = JobPostingSerializer

    def get_queryset(self):
        return (
            JobPosting.objects.prefetch_related("skills")
            .select_related("analysis")
            .all()
        )

    @action(detail=True, methods=["post"], url_path="change-status")
    def change_status(self, request, pk=None):
        job = self.get_object()
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job.application_status = serializer.validated_data["application_status"]
        job.save(update_fields=["application_status", "updated_at"])
        return Response(self.get_serializer(job).data)

    @action(detail=False, methods=["post"], url_path="import-link")
    def import_link(self, request):
        serializer = ImportLinkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = import_job_from_link(serializer.validated_data["url"])
        return Response(
            self.get_serializer(result.job).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="import-text")
    def import_text(self, request):
        serializer = ImportTextSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = import_job_from_text(serializer.validated_data["text"])
        return Response(
            self.get_serializer(result.job).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="import-bulk")
    def import_bulk(self, request):
        serializer = ImportBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        jobs = []
        errors = []

        for url in serializer.validated_data["urls"]:
            url_serializer = ImportLinkSerializer(data={"url": url})
            if not url_serializer.is_valid():
                errors.append({"url": url, "error": url_serializer.errors["url"][0]})
                continue
            result = import_job_from_link(url_serializer.validated_data["url"])
            jobs.append(result.job)

        response_status = status.HTTP_201_CREATED if jobs else status.HTTP_400_BAD_REQUEST
        return Response(
            {
                "results": self.get_serializer(jobs, many=True).data,
                "errors": errors,
            },
            status=response_status,
        )


class JobSkillViewSet(viewsets.ModelViewSet):
    queryset = JobSkill.objects.select_related("job").all()
    serializer_class = JobSkillSerializer


class JobAnalysisViewSet(viewsets.ModelViewSet):
    queryset = JobAnalysis.objects.select_related("job").all()
    serializer_class = JobAnalysisSerializer
