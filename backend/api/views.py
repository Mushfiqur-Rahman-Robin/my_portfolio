import logging

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from openai import OpenAI
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .chromadb_utils import query_nodes
from .models import (
    Achievement,
    Certification,
    ChatMessage,
    ChatSession,
    ContactMessage,
    DailyVisitorCount,
    Experience,
    ExperiencePhoto,
    Project,
    Publication,
    Resume,
    Tag,
    TotalVisitorCount,
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
from .throttles import ChatbotRateThrottle, ContactFormRateThrottle, VisitorCountRateThrottle

# Get an instance of a logger
logger = logging.getLogger(__name__)
email_logger = logging.getLogger("email_sending")


class StandardResultsPagination(PageNumberPagination):
    page_size = 3
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
            # --- UPDATED LOGIC ---
            # 1. Increment the total visitor count
            total_count, _ = TotalVisitorCount.objects.get_or_create()
            total_count.count = F("count") + 1
            total_count.save()
            total_count.refresh_from_db()

            # 2. Increment today's visitor count
            today = timezone.now().date()
            daily_count, created = DailyVisitorCount.objects.get_or_create(date=today)
            if not created:
                daily_count.count = F("count") + 1
                daily_count.save()

            return Response(
                {"message": "Visitor count incremented", "count": total_count.count},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Error incrementing visitor count: {e}", exc_info=True)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatbotView(APIView):
    """
    Handles chatbot queries by retrieving context from ChromaDB
    and generating a response using OpenAI's GPT model.
    """

    authentication_classes = []
    permission_classes = []
    schema_tags = ["Chatbot"]
    throttle_classes = [ChatbotRateThrottle]

    def post(self, request, *args, **kwargs):
        query = request.data.get("query")
        session_id = request.data.get("session_id")

        if not query:
            return Response({"error": "Query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # --- Session Handling ---
            if session_id:
                try:
                    session = ChatSession.objects.get(id=session_id)
                except ChatSession.DoesNotExist:
                    # If frontend provides an invalid/old session ID, create a new one
                    session = ChatSession.objects.create()
            else:
                session = ChatSession.objects.create()

            # Save the user's message
            ChatMessage.objects.create(session=session, sender="user", message=query)

            # --- Smart Context Injection ---
            special_context = []

            # 1. Handle "Latest Experience"
            latest_experience = Experience.objects.order_by("-is_current", "-start_date").first()
            if latest_experience:
                special_context.append(
                    f"Md Mushfiqur Rahman's most recent professional experience is as a "
                    f"{latest_experience.job_title} at {latest_experience.company_name}."
                )

            # 2. Handle "Publications" list
            publications = Publication.objects.all()
            if publications.exists():
                pub_titles = ", ".join([f'"{p.title}"' for p in publications])
                special_context.append(f"He has the following publications: {pub_titles}.")

            # 3. Retrieve general context from ChromaDB
            results = query_nodes(query, n_results=4)
            retrieved_context = "\n\n".join(results["documents"][0]) if results.get("documents") and results["documents"][0] else ""

            # Combine all context
            final_context = "\n\n".join(special_context) + "\n\n" + retrieved_context
            final_context = final_context.strip()

            if not final_context:
                final_context = "No relevant information found in the knowledge base."

            # --- Updated Prompt with Privacy Guardrails ---
            prompt = (
                f"You are a helpful AI assistant for Md Mushfiqur Rahman's personal portfolio website. "
                f"Your tone should be professional, friendly, and concise. "
                f"Answer the user's question based ONLY on the following context. "
                f"If you are asked for a personal phone number, physical address, \
                or any other private contact detail not explicitly listed in the context, \
                you MUST politely refuse and state that the best way to connect is via the professional links like email or LinkedIn."
                f"If the context doesn't contain the answer to a general question, \
                state that you don't have that specific information and suggest they ask about his skills, projects, or experience.\n\n"
                f"Do NOT answer anything that is not related to Md Mushfiqur Rahman's personal portfolio website and personal information.\n\n"
                f"Use bullet points to answer the question when possible.\n\n"
                f"---CONTEXT---\n{final_context}\n\n"
                f"---QUESTION---\n{query}\n\n"
                f"---ANSWER---\n"
            )

            # 4. Call OpenAI API
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            completion = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.2,
            )
            answer = completion.choices[0].message.content

            # Save the bot's response
            ChatMessage.objects.create(session=session, sender="bot", message=answer)

            # --- Return the answer AND the session_id ---
            return Response({"answer": answer, "session_id": str(session.id)}, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Chatbot error: {e}")
            return Response({"error": "An internal error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
