from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

# Import new models and Tag
from .models import Achievement, Certification, ContactMessage, Project, Publication, Resume, Tag, VisitorCount
from .serializers import (
    AchievementSerializer,
    CertificationSerializer,
    ContactMessageSerializer,
    ProjectSerializer,
    PublicationSerializer,
    ResumeSerializer,
    TagSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ProjectViewSet(viewsets.ModelViewSet):  # Changed to ModelViewSet to allow POST/PUT/DELETE
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tag_name = self.request.query_params.get("tag", None)
        if tag_name:
            # Filter projects that have a tag with the given name
            queryset = queryset.filter(tags__name__iexact=tag_name)
        return queryset


class PublicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer


class CertificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer


class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    http_method_names = ["post", "head", "options"]  # Only allow POST requests for new messages


# New ViewSet for Resume (Allowing POST for upload, ReadOnly for retrieval)
class ResumeViewSet(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    # Allow POST for upload, GET for viewing latest resume
    # You might want to restrict uploads to only authenticated users in a real app
    http_method_names = ["get", "post", "head", "options", "delete"]  # Added delete for easier management

    # Optional: ensure only one resume can be active
    def perform_create(self, serializer):
        # Delete old resumes if you only want one active
        Resume.objects.all().delete()
        serializer.save()


class VisitorCountView(APIView):
    authentication_classes = []  # No authentication for this simple counter
    permission_classes = []  # No permissions needed

    def post(self, request, format=None):
        try:
            visitor_count, created = VisitorCount.objects.get_or_create(pk=1)
            # Use pk=1 for a single counter instance
            visitor_count.count += 1
            visitor_count.save()
            return Response({"message": "Visitor count incremented"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # You could add a GET method here for admin or debug purposes if needed
    # def get(self, request, format=None):
    #     try:
    #         visitor_count = VisitorCount.objects.get(pk=1)
    #         return Response({"count": visitor_count.count}, status=status.HTTP_200_OK)
    #     except VisitorCount.DoesNotExist:
    #         return Response({"count": 0}, status=status.HTTP_200_OK)
