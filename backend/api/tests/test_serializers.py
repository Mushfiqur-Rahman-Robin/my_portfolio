from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from ..models import Achievement, Certification, ContactMessage, Experience, ExperiencePhoto, Project, ProjectImage, Publication, Resume, Tag
from ..serializers import (
    AchievementSerializer,
    CertificationSerializer,
    ContactMessageSerializer,
    ExperiencePhotoSerializer,
    ExperienceSerializer,
    ProjectImageSerializer,
    ProjectSerializer,
    PublicationSerializer,
    ResumeSerializer,
    TagSerializer,
    VisitorCountPostSerializer,
    VisitorCountResponseSerializer,
)


def _make_image():
    buf = BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(buf, "png")
    buf.name = "test.png"
    buf.seek(0)
    return SimpleUploadedFile(buf.name, buf.read(), content_type="image/png")


class TagSerializerTests(TestCase):
    def test_serialize_tag(self):
        tag = Tag.objects.create(name="Python")
        data = TagSerializer(tag).data
        self.assertEqual(data["name"], "Python")
        self.assertIsNotNone(data["id"])

    def test_tag_serializer_readonly(self):
        serializer = TagSerializer(data={"name": "Test"})
        self.assertTrue(serializer.is_valid())


class ProjectSerializerTests(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="AI")

    def test_serialize_project(self):
        project = Project.objects.create(title="My Project", description="desc", image=_make_image())
        project.tags.add(self.tag)
        data = ProjectSerializer(project).data
        self.assertEqual(data["title"], "My Project")

    def test_create_project_with_tags(self):
        Tag.objects.get_or_create(name="AI")
        Tag.objects.get_or_create(name="Web")
        data = {"title": "New Project", "description": "desc", "display_order": 1, "tags": ["AI", "Web"], "image": _make_image()}
        serializer = ProjectSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        project = serializer.save()
        self.assertEqual(project.tags.count(), 2)

    def test_create_project_without_tags(self):
        data = {"title": "No Tags", "description": "desc", "image": _make_image()}
        serializer = ProjectSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        project = serializer.save()
        self.assertEqual(project.tags.count(), 0)

    def test_update_project_add_tags(self):
        project = Project.objects.create(title="Old", description="desc", image=_make_image())
        Tag.objects.get_or_create(name="Python")
        data = {"tags": ["Python"]}
        serializer = ProjectSerializer(instance=project, data=data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated = serializer.save()
        self.assertEqual(updated.tags.count(), 1)
        self.assertEqual(updated.tags.first().name, "Python")

    def test_update_project_clear_tags(self):
        project = Project.objects.create(title="Old", description="desc", image=_make_image())
        project.tags.add(self.tag)
        data = {"tags": []}
        serializer = ProjectSerializer(instance=project, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.tags.count(), 0)

    def test_update_project_ignore_tags_when_not_provided(self):
        project = Project.objects.create(title="Old", description="desc", image=_make_image())
        project.tags.add(self.tag)
        data = {"title": "New Title"}
        serializer = ProjectSerializer(instance=project, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.tags.count(), 1)

    def test_nested_gallery_images_read_only(self):
        project = Project.objects.create(title="Gallery Test", description="desc", image=_make_image())
        ProjectImage.objects.create(project=project, image=_make_image(), caption="cap")
        data = ProjectSerializer(project).data
        self.assertEqual(len(data["gallery_images"]), 1)
        self.assertEqual(data["gallery_images"][0]["caption"], "cap")


class PublicationSerializerTests(TestCase):
    def test_serialize_publication(self):
        pub = Publication.objects.create(
            title="Paper",
            authors="A, B",
            conference="Conf",
            publication_url="https://example.com",
            published_date="2024-01-01",
        )
        data = PublicationSerializer(pub).data
        self.assertEqual(data["title"], "Paper")
        self.assertEqual(data["authors"], "A, B")


class CertificationSerializerTests(TestCase):
    def test_serialize_certification(self):
        cert = Certification.objects.create(
            name="AWS",
            issuing_organization="Amazon",
            issue_date="2024-01-01",
        )
        data = CertificationSerializer(cert).data
        self.assertEqual(data["name"], "AWS")


class AchievementSerializerTests(TestCase):
    def test_serialize_achievement(self):
        ach = Achievement.objects.create(title="Winner", description="desc", date="2024-01-01")
        data = AchievementSerializer(ach).data
        self.assertEqual(data["title"], "Winner")


class ContactMessageSerializerTests(TestCase):
    def test_serialize_contact_message(self):
        msg = ContactMessage.objects.create(name="User", email="u@ex.com", message="Hello")
        data = ContactMessageSerializer(msg).data
        self.assertEqual(data["name"], "User")

    def test_sent_at_read_only(self):
        serializer = ContactMessageSerializer(data={"name": "User", "email": "u@ex.com", "message": "Hello"})
        self.assertTrue(serializer.is_valid())
        obj = serializer.save()
        self.assertIsNotNone(obj.sent_at)

    def test_invalid_email(self):
        serializer = ContactMessageSerializer(data={"name": "User", "email": "notanemail", "message": "Hello"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class ResumeSerializerTests(TestCase):
    def test_serialize_resume(self):
        resume = Resume.objects.create(title="CV", pdf_file="resumes/test.pdf")
        data = ResumeSerializer(resume).data
        self.assertEqual(data["title"], "CV")

    def test_uploaded_at_read_only(self):
        resume_file = SimpleUploadedFile("resume.pdf", b"dummy pdf content", content_type="application/pdf")
        serializer = ResumeSerializer(data={"title": "CV", "pdf_file": resume_file})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        obj = serializer.save()
        self.assertIsNotNone(obj.uploaded_at)


class ExperienceSerializerTests(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            company_name="Corp",
            job_title="Engineer",
            start_date="2023-01-01",
            end_date="2024-12-31",
            is_current=False,
            work_details="Built stuff.",
        )

    def test_end_date_display_current(self):
        exp = Experience.objects.create(
            company_name="Current Corp",
            job_title="Lead",
            start_date="2024-01-01",
            is_current=True,
        )
        data = ExperienceSerializer(exp).data
        self.assertEqual(data["end_date_display"], "Present")

    def test_end_date_display_with_date(self):
        self.experience.refresh_from_db()
        data = ExperienceSerializer(self.experience).data
        self.assertEqual(data["end_date_display"], "Dec. 2024")

    def test_end_date_display_no_date_not_current(self):
        exp = Experience.objects.create(company_name="Old", start_date="2020-01-01", is_current=False)
        data = ExperienceSerializer(exp).data
        self.assertEqual(data["end_date_display"], "")

    def test_nested_photos_read_only(self):
        self.experience.refresh_from_db()
        ExperiencePhoto.objects.create(experience=self.experience, image="experience/memories/test.webp", caption="pic")
        data = ExperienceSerializer(self.experience).data
        self.assertEqual(len(data["photos"]), 1)
        self.assertEqual(data["photos"][0]["caption"], "pic")

    def test_serialize_experience_basic(self):
        self.experience.refresh_from_db()
        data = ExperienceSerializer(self.experience).data
        self.assertEqual(data["company_name"], "Corp")
        self.assertEqual(data["job_title"], "Engineer")


class ExperiencePhotoSerializerTests(TestCase):
    def test_serialize_experience_photo(self):
        exp = Experience.objects.create(company_name="Corp", start_date="2023-01-01")
        photo = ExperiencePhoto.objects.create(experience=exp, image="experience/memories/test.webp", caption="Team")
        data = ExperiencePhotoSerializer(photo).data
        self.assertEqual(data["caption"], "Team")


class ProjectImageSerializerTests(TestCase):
    def test_serialize_project_image(self):
        project = Project.objects.create(title="Test", description="desc", image=_make_image())
        pi = ProjectImage.objects.create(project=project, image=_make_image(), caption="Hero")
        data = ProjectImageSerializer(pi).data
        self.assertEqual(data["caption"], "Hero")


class VisitorCountSerializerTests(TestCase):
    def test_post_serializer_empty_input(self):
        serializer = VisitorCountPostSerializer(data={})
        self.assertTrue(serializer.is_valid())

    def test_response_serializer(self):
        serializer = VisitorCountResponseSerializer({"message": "ok", "count": 42})
        self.assertEqual(serializer.data["message"], "ok")
        self.assertEqual(serializer.data["count"], 42)
