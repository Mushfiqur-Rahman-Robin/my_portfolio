# backend/api/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

# Import all viewsets
from .views import (
    AchievementViewSet,
    CertificationViewSet,
    ContactMessageViewSet,
    ExperiencePhotoViewSet,
    ExperienceViewSet,
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
router.register(r"experiences", ExperienceViewSet, basename="experience")
router.register(r"experience-photos", ExperiencePhotoViewSet, basename="experience-photo")
urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/visitor-count/", VisitorCountView.as_view(), name="visitor-count"),
]
