from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ListField, URLField, CharField, Serializer

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
    import_jobs_from_links,
)


class ImportLinkSerializer(Serializer):
    url = URLField()


class ImportTextSerializer(Serializer):
    text = CharField(allow_blank=False, trim_whitespace=True)


class ImportBulkSerializer(Serializer):
    urls = ListField(child=URLField(), allow_empty=False)


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
        results = import_jobs_from_links(serializer.validated_data["urls"])
        jobs = [result.job for result in results]
        return Response(
            self.get_serializer(jobs, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class JobSkillViewSet(viewsets.ModelViewSet):
    queryset = JobSkill.objects.select_related("job").all()
    serializer_class = JobSkillSerializer


class JobAnalysisViewSet(viewsets.ModelViewSet):
    queryset = JobAnalysis.objects.select_related("job").all()
    serializer_class = JobAnalysisSerializer
