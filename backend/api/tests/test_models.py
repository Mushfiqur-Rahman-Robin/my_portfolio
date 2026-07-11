import datetime

from django.test import TestCase

from ..models import (
    Achievement,
    Certification,
    ChatMessage,
    ChatSession,
    ContactMessage,
    DailyVisitorCount,
    Experience,
    ExperiencePhoto,
    LLMCostTracking,
    Project,
    ProjectImage,
    Publication,
    Resume,
    Tag,
    TotalVisitorCount,
    VisitorAnalytics,
)


class ModelStrTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tag = Tag.objects.create(name="Django")
        cls.project = Project.objects.create(title="AI Dashboard", description="<p>desc</p>", image="projects/banners/test.webp")
        cls.project.tags.add(cls.tag)
        cls.project_image = ProjectImage.objects.create(project=cls.project, image="projects/gallery/test.webp", caption="hero")
        cls.publication = Publication.objects.create(
            title="Deep Learning",
            authors="Author et al.",
            conference="NeurIPS",
            publication_url="https://example.com",
            published_date="2024-07-01",
        )
        cls.certification = Certification.objects.create(
            name="AWS ML Specialty",
            issuing_organization="AWS",
            credential_url="https://example.com",
            issue_date="2024-06-15",
        )
        cls.achievement = Achievement.objects.create(title="Top 10% Kaggle", description="Placed top 10%", date="2024-05-20")
        cls.contact_message = ContactMessage.objects.create(name="Jane", email="jane@example.com", message="Hello")
        cls.resume = Resume.objects.create(title="Resume 2024", pdf_file="resumes/test.pdf")
        cls.total_visitor = TotalVisitorCount.objects.create(count=42)
        cls.daily_visitor = DailyVisitorCount.objects.create(date=datetime.date(2024, 7, 1), count=5)
        cls.visitor_analytics = VisitorAnalytics.objects.create(
            ip_address="203.0.113.1",
            country="Bangladesh",
            device_type="desktop",
            user_agent="Mozilla/5.0",
        )
        cls.experience = Experience.objects.create(
            company_name="Acme Corp",
            job_title="ML Engineer",
            start_date="2023-01-01",
            end_date="2024-12-31",
            is_current=False,
            work_details="Built pipelines.",
        )
        cls.experience_photo = ExperiencePhoto.objects.create(experience=cls.experience, image="experience/memories/test.webp", caption="Team photo")
        cls.chat_session = ChatSession.objects.create()
        cls.chat_message = ChatMessage.objects.create(session=cls.chat_session, sender="user", message="Hi")
        cls.llm_cost = LLMCostTracking.objects.create(
            operation_type="chat",
            model_name="gemini-2.5-flash",
            session_total_tokens=200,
            session_cost=0.0010,
            total_cost=0.0050,
        )

    def test_tag_str(self):
        self.assertEqual(str(self.tag), "Django")

    def test_project_str(self):
        self.assertEqual(str(self.project), "AI Dashboard")

    def test_project_image_str_with_caption(self):
        self.assertIn("AI Dashboard", str(self.project_image))
        self.assertIn("hero", str(self.project_image))

    def test_project_image_str_without_caption(self):
        pi = ProjectImage.objects.create(project=self.project, image="projects/gallery/no_cap.webp")
        self.assertIn("AI Dashboard", str(pi))
        self.assertIn("no_cap.webp", str(pi))

    def test_publication_str(self):
        self.assertEqual(str(self.publication), "Deep Learning")

    def test_certification_str(self):
        self.assertEqual(str(self.certification), "AWS ML Specialty")

    def test_achievement_str(self):
        self.assertEqual(str(self.achievement), "Top 10% Kaggle")

    def test_contact_message_str(self):
        s = str(self.contact_message)
        self.assertIn("Jane", s)
        self.assertIn("jane@example.com", s)

    def test_resume_str(self):
        self.assertEqual(str(self.resume), "Resume 2024")

    def test_total_visitor_count_str(self):
        self.assertEqual(str(self.total_visitor), "Total Visitors: 42")

    def test_daily_visitor_count_str(self):
        self.assertIn("2024-07-01", str(self.daily_visitor))
        self.assertIn("5 visitors", str(self.daily_visitor))

    def test_visitor_analytics_str(self):
        s = str(self.visitor_analytics)
        self.assertIn("203.0.113.1", s)
        self.assertIn("Bangladesh", s)
        self.assertIn("Desktop/Laptop", s)

    def test_visitor_analytics_str_unknown_ip(self):
        va = VisitorAnalytics.objects.create(country="France", device_type="mobile")
        self.assertIn("Unknown IP", str(va))
        self.assertIn("Mobile", str(va))

    def test_experience_str(self):
        self.assertEqual(str(self.experience), "ML Engineer at Acme Corp")

    def test_experience_str_no_job_title(self):
        exp = Experience.objects.create(company_name="Startup", start_date="2022-01-01")
        self.assertEqual(str(exp), " at Startup")

    def test_experience_photo_str_with_caption(self):
        s = str(self.experience_photo)
        self.assertIn("Acme Corp", s)
        self.assertIn("Team photo", s)

    def test_experience_photo_str_without_caption(self):
        ep = ExperiencePhoto.objects.create(experience=self.experience, image="experience/memories/pic.webp")
        self.assertIn("pic.webp", str(ep))

    def test_chat_session_str(self):
        self.assertIn(str(self.chat_session.id), str(self.chat_session))

    def test_chat_message_str(self):
        s = str(self.chat_message)
        self.assertIn("User", s)

    def test_chat_message_str_bot(self):
        msg = ChatMessage.objects.create(session=self.chat_session, sender="bot", message="Hello")
        self.assertIn("Bot", str(msg))

    def test_llm_cost_tracking_str(self):
        s = str(self.llm_cost)
        self.assertIn("Chat", s)
        self.assertIn("0.001", s)
        self.assertIn("0.005", s)

    def test_llm_cost_tracking_str_embedding(self):
        record = LLMCostTracking.objects.create(
            operation_type="embedding",
            model_name="text-embedding-3-small",
            session_total_tokens=100,
            session_cost=0.0002,
            total_cost=0.0008,
        )
        s = str(record)
        self.assertIn("Embedding", s)
        self.assertIn("0.0002", s)


class ModelMetaTests(TestCase):
    def test_project_ordering(self):
        self.assertEqual(Project._meta.ordering, ["display_order", "-created_at"])

    def test_publication_ordering(self):
        self.assertEqual(Publication._meta.ordering, ["display_order", "-published_date"])

    def test_certification_ordering(self):
        self.assertEqual(Certification._meta.ordering, ["display_order", "-issue_date"])

    def test_achievement_ordering(self):
        self.assertEqual(Achievement._meta.ordering, ["display_order", "-date"])

    def test_contact_message_ordering(self):
        self.assertEqual(ContactMessage._meta.ordering, ["-sent_at"])

    def test_resume_ordering(self):
        self.assertEqual(Resume._meta.ordering, ["-uploaded_at"])

    def test_daily_visitor_ordering(self):
        self.assertEqual(DailyVisitorCount._meta.ordering, ["-date"])

    def test_visitor_analytics_ordering(self):
        self.assertEqual(VisitorAnalytics._meta.ordering, ["-visited_at"])

    def test_experience_ordering(self):
        self.assertEqual(Experience._meta.ordering, ["display_order", "-start_date"])

    def test_experience_photo_ordering(self):
        self.assertEqual(ExperiencePhoto._meta.ordering, ["display_order"])

    def test_chat_session_ordering(self):
        self.assertEqual(ChatSession._meta.ordering, ["-created_at"])

    def test_chat_message_ordering(self):
        self.assertEqual(ChatMessage._meta.ordering, ["created_at"])

    def test_llm_cost_tracking_ordering(self):
        self.assertEqual(LLMCostTracking._meta.ordering, ["-updated_at"])

    def test_verbose_names(self):
        self.assertEqual(Project._meta.verbose_name, "Project")
        self.assertEqual(Project._meta.verbose_name_plural, "Projects")
        self.assertEqual(Publication._meta.verbose_name, "Publication")
        self.assertEqual(Certification._meta.verbose_name, "Certification")
        self.assertEqual(Achievement._meta.verbose_name, "Achievement")
        self.assertEqual(ContactMessage._meta.verbose_name, "Contact Message")
        self.assertEqual(Experience._meta.verbose_name, "Professional Experience")

    def test_uuid_primary_keys(self):
        for model_cls in [
            Tag,
            Project,
            ProjectImage,
            Publication,
            Certification,
            Achievement,
            ContactMessage,
            Resume,
            Experience,
            ExperiencePhoto,
            ChatSession,
            ChatMessage,
            LLMCostTracking,
        ]:
            pk_field = model_cls._meta.pk
            self.assertFalse(pk_field.editable)
            self.assertIsNotNone(getattr(pk_field, "default", None))

    def test_project_many_to_many_tags(self):
        tag1 = Tag.objects.create(name="Python")
        tag2 = Tag.objects.create(name="AI")
        self.project = Project.objects.create(title="ML Project", description="desc", image="projects/banners/test.webp")
        self.project.tags.add(tag1, tag2)
        self.assertEqual(self.project.tags.count(), 2)

    def test_project_gallery_images_relation(self):
        project = Project.objects.create(title="Test", description="desc", image="projects/banners/test.webp")
        img = ProjectImage.objects.create(project=project, image="projects/gallery/test.webp")
        self.assertEqual(project.gallery_images.count(), 1)
        self.assertEqual(project.gallery_images.first(), img)

    def test_experience_photos_relation(self):
        exp = Experience.objects.create(company_name="Corp", start_date="2023-01-01")
        photo = ExperiencePhoto.objects.create(experience=exp, image="experience/memories/test.webp")
        self.assertEqual(exp.photos.count(), 1)
        self.assertEqual(exp.photos.first(), photo)

    def test_chat_session_messages_relation(self):
        session = ChatSession.objects.create()
        msg = ChatMessage.objects.create(session=session, sender="user", message="Hi")
        self.assertEqual(session.messages.count(), 1)
        self.assertEqual(session.messages.first(), msg)

    def test_is_current_default_false(self):
        exp = Experience.objects.create(company_name="Startup", start_date="2023-01-01")
        self.assertFalse(exp.is_current)

    def test_experience_job_title_blank(self):
        exp = Experience.objects.create(company_name="Startup", start_date="2023-01-01")
        self.assertEqual(exp.job_title, "")

    def test_certification_nullable_fields(self):
        cert = Certification.objects.create(name="Test", issuing_organization="Org", issue_date="2024-01-01")
        self.assertIsNone(cert.credential_url)
        self.assertFalse(cert.image)

    def test_publication_url_required(self):
        pub = Publication.objects.create(
            title="Test",
            authors="Author",
            conference="Conf",
            publication_url="https://example.com",
            published_date="2024-01-01",
        )
        self.assertEqual(pub.publication_url, "https://example.com")

    def test_total_visitor_count_fixed_uuid(self):
        tv = TotalVisitorCount.objects.create(count=1)
        expected_uuid = "1a2b3c4d-e5f6-7890-1234-567890abcdef"
        self.assertEqual(str(tv.id), expected_uuid)

    def test_daily_visitor_count_unique_date(self):
        DailyVisitorCount.objects.create(date=datetime.date(2024, 8, 1), count=3)
        with self.assertRaises(Exception):
            DailyVisitorCount.objects.create(date=datetime.date(2024, 8, 1), count=5)


class ModelFieldDefaultsTests(TestCase):
    def test_project_display_order_default(self):
        p = Project.objects.create(title="Test", description="desc", image="projects/banners/test.webp")
        self.assertEqual(p.display_order, 0)

    def test_project_is_featured_default(self):
        p = Project.objects.create(title="Test", description="desc", image="projects/banners/test.webp")
        self.assertFalse(p.is_featured)

    def test_visitor_analytics_defaults(self):
        va = VisitorAnalytics.objects.create()
        self.assertEqual(va.country, "Unknown")
        self.assertEqual(va.device_type, "unknown")
        self.assertEqual(va.user_agent, "")

    def test_llm_cost_tracking_defaults(self):
        record = LLMCostTracking.objects.create(session_total_tokens=10)
        self.assertEqual(record.operation_type, "chat")
        self.assertEqual(record.model_name, "unknown")
        self.assertEqual(record.session_total_tokens, 10)
        self.assertEqual(float(record.session_cost), 0.0)

    def test_experience_end_date_nullable(self):
        exp = Experience.objects.create(
            company_name="Current Inc",
            job_title="Lead",
            start_date="2023-01-01",
            is_current=True,
        )
        self.assertIsNone(exp.end_date)
