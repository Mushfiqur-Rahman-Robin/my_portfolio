import uuid

from django.db.models import F
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Achievement,
    Certification,
    ContactMessage,
    Experience,
    ExperiencePhoto,
    Project,
    Publication,
    Resume,
    Tag,
    VisitorCount,
)
from .serializers import (
    AchievementSerializer,
    CertificationSerializer,
    ContactMessageSerializer,
    ExperiencePhotoSerializer,
    ExperienceSerializer,
    ProjectSerializer,
    PublicationSerializer,
    ResumeSerializer,
    TagSerializer,
    VisitorCountPostSerializer,
    VisitorCountResponseSerializer,
)


class StandardResultsPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100


class ExperienceResultsPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    schema_tags = ["Portfolio Management - Tags"]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = StandardResultsPagination
    schema_tags = ["Portfolio Management - Projects"]

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_name = self.request.query_params.get("tag", None)
        is_featured = self.request.query_params.get("is_featured", None)

        if tag_name:
            queryset = queryset.filter(tags__name__iexact=tag_name)

        # Correctly convert string 'true'/'false' to boolean True/False
        if is_featured is not None:
            if is_featured.lower() == "true":
                queryset = queryset.filter(is_featured=True)
            elif is_featured.lower() == "false":
                queryset = queryset.filter(is_featured=False)
            # If is_featured is present but not 'true'/'false', then return empty or no filter.
            # For this case, we just won't apply the filter if it's invalid.

        return queryset.order_by("display_order", "-created_at")


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    pagination_class = StandardResultsPagination
    schema_tags = ["Portfolio Management - Publications"]


class CertificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    pagination_class = StandardResultsPagination
    schema_tags = ["Portfolio Management - Certifications"]


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    pagination_class = StandardResultsPagination
    schema_tags = ["Portfolio Management - Achievements"]


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    http_method_names = ["post", "head", "options"]
    schema_tags = ["Contact & Admin"]


class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    http_method_names = ["get", "post", "head", "options", "delete"]
    schema_tags = ["Contact & Admin"]

    def perform_create(self, serializer):
        Resume.objects.all().delete()
        serializer.save()


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    pagination_class = ExperienceResultsPagination
    http_method_names = ["get", "post", "head", "options"]
    schema_tags = ["Portfolio Management - Experiences"]


class ExperiencePhotoViewSet(viewsets.ModelViewSet):
    queryset = ExperiencePhoto.objects.all()
    serializer_class = ExperiencePhotoSerializer
    http_method_names = ["get", "post", "head", "options", "delete"]
    schema_tags = ["Portfolio Management - Experiences"]


class VisitorCountView(APIView):
    authentication_classes = []
    permission_classes = []
    schema_tags = ["Contact & Admin"]

    @extend_schema(
        request=VisitorCountPostSerializer,  # Specify the input serializer (empty, as no body is expected)
        responses={200: VisitorCountResponseSerializer},  # Specify the output serializer for 200 OK
        summary="Increment and get total visitor count",
    )
    def post(self, request, format=None):
        try:
            pk = uuid.UUID("1a2b3c4d-e5f6-7890-1234-567890abcdef")
            visitor_count, created = VisitorCount.objects.get_or_create(pk=pk)
            visitor_count.count = F("count") + 1
            visitor_count.save()
            visitor_count.refresh_from_db()
            return Response(
                {"message": "Visitor count incremented", "count": visitor_count.count},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
