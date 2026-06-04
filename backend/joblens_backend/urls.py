from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from documents.views import ProfileDocumentViewSet
from jobs.views import JobAnalysisViewSet, JobPostingViewSet, JobSkillViewSet
from profiles.views import ProfileSkillViewSet, UserProfileViewSet

router = DefaultRouter()
router.register("jobs", JobPostingViewSet, basename="job")
router.register("job-skills", JobSkillViewSet, basename="job-skill")
router.register("job-analyses", JobAnalysisViewSet, basename="job-analysis")
router.register("profiles", UserProfileViewSet, basename="profile")
router.register("profile-skills", ProfileSkillViewSet, basename="profile-skill")
router.register("documents", ProfileDocumentViewSet, basename="document")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
