import logging
import uuid

from django.conf import settings
from django.core.mail import send_mail
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
from .throttles import ContactFormRateThrottle, VisitorCountRateThrottle

# Get an instance of a logger
logger = logging.getLogger(__name__)
email_logger = logging.getLogger("email_sending")


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

        if is_featured is not None:
            if is_featured.lower() == "true":
                queryset = queryset.filter(is_featured=True)
            elif is_featured.lower() == "false":
                queryset = queryset.filter(is_featured=False)
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
    throttle_classes = [ContactFormRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Extract data for email
        name = serializer.validated_data.get("name")
        email = serializer.validated_data.get("email")
        message_text = serializer.validated_data.get("message")

        # Send email notification
        subject = "New Contact Message from Portfolio Website"
        message_body = (
            f"You have received a new message from your portfolio website:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Message:\n{message_text}\n\n"
            f"Please respond to {name} at {email} directly."
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.ADMIN_EMAIL]  # Send to your admin email

        try:
            send_mail(subject, message_body, from_email, recipient_list, fail_silently=False)
            email_logger.info(f"Email sent for new contact message from {email}")
        except Exception as e:
            email_logger.error(f"Failed to send email for contact message from {email}: {e}", exc_info=True)
            # Log the error but don't fail the API request

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    http_method_names = ["get", "post", "head", "options", "delete"]
    schema_tags = ["Contact & Admin"]


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
    throttle_classes = [VisitorCountRateThrottle]

    @extend_schema(
        request=VisitorCountPostSerializer,
        responses={200: VisitorCountResponseSerializer},
        summary="Increment and get total visitor count",
    )
    def post(self, request, format=None):
        try:
            # Use a fixed UUID for the single VisitorCount entry
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
            logger.error(f"Error incrementing visitor count: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
