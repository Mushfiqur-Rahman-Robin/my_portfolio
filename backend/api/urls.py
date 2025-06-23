# backend/api/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Import new views and TagViewSet
from .views import (
    AchievementViewSet,
    CertificationViewSet,
    ContactMessageViewSet,
    ProjectViewSet,
    PublicationViewSet,
    ResumeViewSet,
    TagViewSet,
    VisitorCountView,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"publications", PublicationViewSet, basename="publication")
router.register(r"certifications", CertificationViewSet, basename="certification")
router.register(r"achievements", AchievementViewSet, basename="achievement")
router.register(r"messages", ContactMessageViewSet, basename="message")
router.register(r"resumes", ResumeViewSet, basename="resume")
router.register(r"tags", TagViewSet, basename="tag")

urlpatterns = [
    # Only include your API endpoints here
    path("v1/", include(router.urls)),
    path("v1/visitor-count/", VisitorCountView.as_view(), name="visitor-count"),
]
