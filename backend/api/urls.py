# backend/api/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AchievementViewSet, CertificationViewSet, ProjectViewSet, PublicationViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"publications", PublicationViewSet, basename="publication")
router.register(r"certifications", CertificationViewSet, basename="certification")
router.register(r"achievements", AchievementViewSet, basename="achievement")

urlpatterns = [
    # Only include your API endpoints here
    path("v1/", include(router.urls)),
]
