import os
from io import BytesIO
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from ..models import Achievement, Certification, Experience, ExperiencePhoto, Project, ProjectImage, Publication, Resume
from ..signals import convert_new_image_if_needed, delete_file_if_exists, get_doc_id, get_metadata, run_when_chroma_enabled


def _make_image(name="test.png"):
    buf = BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(buf, "png")
    buf.name = name
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/png")


# ---------- Pure helper function tests ----------


class GetDocIdTests(TestCase):
    def test_get_doc_id(self):
        project = Project.objects.create(title="Test", description="desc", image=_make_image())
        doc_id = get_doc_id(project)
        self.assertTrue(doc_id.startswith("project-"))
        self.assertIn(str(project.id), doc_id)

    def test_get_doc_id_experience(self):
        exp = Experience.objects.create(company_name="Corp", start_date="2023-01-01")
        self.assertTrue(get_doc_id(exp).startswith("experience-"))


class GetMetadataTests(TestCase):
    def test_default_title_field(self):
        project = Project.objects.create(title="My Title", description="desc", image=_make_image())
        meta = get_metadata(project, url_path="projects")
        self.assertEqual(meta["type"], "project")
        self.assertEqual(meta["title"], "My Title")
        self.assertIn("projects", meta["url"])

    def test_custom_title_field(self):
        cert = Certification.objects.create(name="Cert Name", issuing_organization="Org", issue_date="2024-01-01")
        meta = get_metadata(cert, title_field="name", url_path="certifications")
        self.assertEqual(meta["title"], "Cert Name")

    def test_empty_url_path(self):
        project = Project.objects.create(title="Test", description="desc", image=_make_image())
        meta = get_metadata(project)
        self.assertEqual(meta["url"], "")

    def test_fallback_to_name_field(self):
        cert = Certification.objects.create(name="MyCert", issuing_organization="Org", issue_date="2024-01-01")
        meta = get_metadata(cert)
        self.assertEqual(meta["title"], "MyCert")


class RunWhenChromaEnabledTests(TestCase):
    def test_runs_when_enabled(self):
        call_count = 0

        @run_when_chroma_enabled
        def my_handler(sender, instance, **kwargs):
            nonlocal call_count
            call_count += 1

        with override_settings(ENABLE_CHROMA_SYNC=True):
            my_handler(None, None)

        self.assertEqual(call_count, 1)

    def test_skips_when_disabled(self):
        call_count = 0

        @run_when_chroma_enabled
        def my_handler(sender, instance, **kwargs):
            nonlocal call_count
            call_count += 1

        with override_settings(ENABLE_CHROMA_SYNC=False):
            my_handler(None, None)

        self.assertEqual(call_count, 0)

    def test_passes_args_and_kwargs(self):
        captured = {}

        @run_when_chroma_enabled
        def my_handler(sender, instance, **kwargs):
            captured["sender"] = sender
            captured["instance"] = instance
            captured["kw"] = kwargs

        with override_settings(ENABLE_CHROMA_SYNC=True):
            my_handler("s", "i", extra="val")

        self.assertEqual(captured["sender"], "s")
        self.assertEqual(captured["instance"], "i")
        self.assertEqual(captured["kw"]["extra"], "val")


class DeleteFileIfExistsTests(TestCase):
    def setUp(self):
        self.test_file_path = os.path.join(default_storage.location, "test_delete.txt")
        with open(self.test_file_path, "w") as f:
            f.write("delete me")

    def tearDown(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def test_deletes_existing_file(self):
        self.assertTrue(os.path.exists(self.test_file_path))
        field_mock = MagicMock()
        field_mock.path = self.test_file_path
        delete_file_if_exists(field_mock)
        self.assertFalse(os.path.exists(self.test_file_path))

    def test_no_error_if_file_not_exists(self):
        field_mock = MagicMock()
        field_mock.path = "/nonexistent/file/path.txt"
        delete_file_if_exists(field_mock)

    def test_no_error_if_no_path_attribute(self):
        field_mock = MagicMock(spec=[])
        delete_file_if_exists(field_mock)


class ConvertNewImageIfNeededTests(TestCase):
    def test_converts_new_image(self):
        project = Project(title="Test", description="desc")
        image = _make_image()

        project.image = image
        project.image._committed = False

        convert_new_image_if_needed(project)
        self.assertTrue(project.image.name.endswith(".webp"))

    def test_skips_committed_image(self):
        project = Project(title="Test", description="desc")
        image = _make_image()

        project.image = image
        project.image._committed = True

        convert_new_image_if_needed(project)
        self.assertTrue(project.image.name.endswith(".png"))

    def test_skips_when_no_image(self):
        project = Project(title="Test", description="desc")
        convert_new_image_if_needed(project)

    def test_custom_field_name(self):
        project = Project(title="Test", description="desc")
        image = _make_image()

        project.image = image
        project.image._committed = False

        convert_new_image_if_needed(project, field_name="image")
        self.assertTrue(project.image.name.endswith(".webp"))


# ---------- ChromaDB signal tests with mocking ----------


@override_settings(ENABLE_CHROMA_SYNC=True)
class ChromaDBSignalTests(TestCase):
    def setUp(self):
        self.image = _make_image()

    @patch("api.signals.add_or_update_node")
    def test_sync_project_on_create(self, mock_add):
        Project.objects.create(title="Test Project", description="<p>description</p>", image=self.image)
        mock_add.assert_called_once()
        args = mock_add.call_args[0]
        self.assertIn("project-", args[0])
        self.assertIn("Test Project", args[1])

    @patch("api.signals.add_or_update_node")
    def test_sync_project_on_update(self, mock_add):
        project = Project.objects.create(title="Initial", description="<p>desc</p>", image=self.image)
        mock_add.reset_mock()
        project.title = "Updated"
        project.save()
        mock_add.assert_called_once()
        self.assertIn("Updated", mock_add.call_args[0][1])

    @patch("api.signals.delete_node")
    @patch("api.signals.add_or_update_node")
    def test_delete_project_chroma(self, mock_add, mock_delete):
        project = Project.objects.create(title="To Delete", description="<p>desc</p>", image=self.image)
        project.delete()
        mock_delete.assert_called_once()

    @patch("api.signals.add_or_update_node")
    def test_sync_certification_on_create(self, mock_add):
        Certification.objects.create(name="AWS", issuing_organization="Amazon", issue_date="2024-01-01")
        mock_add.assert_called_once()

    @patch("api.signals.delete_node")
    @patch("api.signals.add_or_update_node")
    def test_delete_certification_chroma(self, mock_add, mock_delete):
        cert = Certification.objects.create(name="AWS", issuing_organization="Amazon", issue_date="2024-01-01")
        cert.delete()
        mock_delete.assert_called_once()

    @patch("api.signals.add_or_update_node")
    def test_sync_publication_on_create(self, mock_add):
        Publication.objects.create(
            title="Paper",
            authors="A, B",
            conference="Conf",
            publication_url="https://example.com",
            published_date="2024-01-01",
        )
        mock_add.assert_called_once()

    @patch("api.signals.delete_node")
    @patch("api.signals.add_or_update_node")
    def test_delete_publication_chroma(self, mock_add, mock_delete):
        pub = Publication.objects.create(
            title="Paper",
            authors="A, B",
            conference="Conf",
            publication_url="https://example.com",
            published_date="2024-01-01",
        )
        pub.delete()
        mock_delete.assert_called_once()

    @patch("api.signals.add_or_update_node")
    def test_sync_achievement_on_create(self, mock_add):
        Achievement.objects.create(title="Achievement", description="desc", date="2024-01-01")
        mock_add.assert_called_once()

    @patch("api.signals.delete_node")
    @patch("api.signals.add_or_update_node")
    def test_delete_achievement_chroma(self, mock_add, mock_delete):
        ach = Achievement.objects.create(title="Achievement", description="desc", date="2024-01-01")
        ach.delete()
        mock_delete.assert_called_once()

    @patch("api.signals.add_or_update_node")
    def test_sync_experience_on_create(self, mock_add):
        Experience.objects.create(
            company_name="Corp",
            job_title="Eng",
            start_date="2024-01-01",
            work_details="Details",
        )
        mock_add.assert_called_once()

    @patch("api.signals.delete_node")
    @patch("api.signals.add_or_update_node")
    def test_delete_experience_chroma(self, mock_add, mock_delete):
        exp = Experience.objects.create(company_name="Corp", start_date="2024-01-01")
        exp.delete()
        mock_delete.assert_called_once()

    @patch("api.signals.add_or_update_node")
    @patch("api.signals.extract_pdf_text", return_value="PDF content")
    @patch("os.path.exists", return_value=True)
    def test_sync_resume_on_create(self, mock_exists, mock_extract, mock_add):
        resume_file = SimpleUploadedFile("resume.pdf", b"pdf content", content_type="application/pdf")
        Resume.objects.create(title="Resume", pdf_file=resume_file)
        mock_add.assert_called_once()

    @patch("api.signals.add_or_update_node")
    @patch("api.signals.extract_pdf_text", return_value="")
    @patch("os.path.exists", return_value=True)
    def test_sync_resume_no_text_extracted(self, mock_exists, mock_extract, mock_add):
        resume_file = SimpleUploadedFile("resume.pdf", b"pdf content", content_type="application/pdf")
        Resume.objects.create(title="Resume", pdf_file=resume_file)
        mock_add.assert_not_called()

    @patch("api.signals.add_or_update_node")
    @patch("api.signals.extract_pdf_text")
    @patch("os.path.exists", return_value=False)
    def test_sync_resume_file_missing(self, mock_exists, mock_extract, mock_add):
        resume_file = SimpleUploadedFile("resume.pdf", b"pdf content", content_type="application/pdf")
        Resume.objects.create(title="Resume", pdf_file=resume_file)
        mock_add.assert_not_called()

    @patch("api.signals.delete_node")
    @patch("api.signals.add_or_update_node")
    @patch("api.signals.extract_pdf_text", return_value="PDF content")
    @patch("os.path.exists", return_value=True)
    def test_delete_resume_chroma(self, mock_exists, mock_extract, mock_add, mock_delete):
        resume_file = SimpleUploadedFile("resume.pdf", b"pdf content", content_type="application/pdf")
        resume = Resume.objects.create(title="Resume", pdf_file=resume_file)
        resume.delete()
        mock_delete.assert_called_once()

    @patch("api.signals.add_or_update_node")
    @patch("api.signals.delete_node")
    def test_sync_resume_deletes_other_resumes(self, mock_delete, mock_add):
        with patch("os.path.exists", return_value=True), patch("api.signals.extract_pdf_text", return_value="content"):
            resume_file1 = SimpleUploadedFile("r1.pdf", b"pdf1", content_type="application/pdf")
            Resume.objects.create(title="Resume 1", pdf_file=resume_file1)
            mock_add.reset_mock()
            mock_delete.reset_mock()

            resume_file2 = SimpleUploadedFile("r2.pdf", b"pdf2", content_type="application/pdf")
            Resume.objects.create(title="Resume 2", pdf_file=resume_file2)

        mock_delete.assert_called_once()
        mock_add.assert_called_once()

    @override_settings(ENABLE_CHROMA_SYNC=False)
    @patch("api.signals.add_or_update_node")
    def test_chroma_sync_skipped_when_disabled(self, mock_add):
        Project.objects.create(title="Test", description="<p>desc</p>", image=self.image)
        mock_add.assert_not_called()


# ---------- File deletion signal tests ----------

TEST_MEDIA_SIGNALS = os.path.join(settings.BASE_DIR, "test_media_signals")


@override_settings(MEDIA_ROOT=TEST_MEDIA_SIGNALS)
class FileDeletionSignalTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        os.makedirs(TEST_MEDIA_SIGNALS, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        import shutil

        shutil.rmtree(TEST_MEDIA_SIGNALS, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.image = _make_image()

    def test_project_delete_removes_file(self):
        project = Project.objects.create(title="File Test", description="desc", image=self.image)
        file_path = project.image.path
        self.assertTrue(os.path.exists(file_path))
        project.delete()
        self.assertFalse(os.path.exists(file_path))

    def test_project_image_delete_removes_file(self):
        project = Project.objects.create(title="File Test", description="desc", image=self.image)
        img = _make_image()
        pi = ProjectImage.objects.create(project=project, image=img)
        file_path = pi.image.path
        self.assertTrue(os.path.exists(file_path))
        pi.delete()
        self.assertFalse(os.path.exists(file_path))

    def test_certification_delete_removes_file(self):
        cert_img = _make_image()
        cert = Certification.objects.create(
            name="Cert",
            issuing_organization="Org",
            issue_date="2024-01-01",
            image=cert_img,
        )
        file_path = cert.image.path
        self.assertTrue(os.path.exists(file_path))
        cert.delete()
        self.assertFalse(os.path.exists(file_path))

    def test_achievement_delete_removes_file(self):
        ach_img = _make_image()
        ach = Achievement.objects.create(title="Achievement", description="desc", date="2024-01-01", image=ach_img)
        file_path = ach.image.path
        self.assertTrue(os.path.exists(file_path))
        ach.delete()
        self.assertFalse(os.path.exists(file_path))

    def test_experience_photo_delete_removes_file(self):
        exp = Experience.objects.create(company_name="Corp", start_date="2024-01-01")
        photo_img = _make_image()
        photo = ExperiencePhoto.objects.create(experience=exp, image=photo_img)
        file_path = photo.image.path
        self.assertTrue(os.path.exists(file_path))
        photo.delete()
        self.assertFalse(os.path.exists(file_path))

    def test_resume_delete_removes_file(self):
        resume_file = SimpleUploadedFile("resume.pdf", b"pdf content", content_type="application/pdf")
        resume = Resume.objects.create(title="Resume", pdf_file=resume_file)
        file_path = resume.pdf_file.path
        self.assertTrue(os.path.exists(file_path))
        resume.delete()
        self.assertFalse(os.path.exists(file_path))

    def test_project_update_replaces_old_image(self):
        project = Project.objects.create(title="File Test", description="desc", image=self.image)
        old_path = project.image.path
        self.assertTrue(os.path.exists(old_path))

        new_img = _make_image(name="new_image.png")
        project.image = new_img
        project.save()

        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(project.image.path))

    def test_project_image_update_replaces_old(self):
        project = Project.objects.create(title="File Test", description="desc", image=self.image)
        old_img = _make_image()
        pi = ProjectImage.objects.create(project=project, image=old_img)
        old_path = pi.image.path
        self.assertTrue(os.path.exists(old_path))

        new_img = _make_image(name="new_gallery.png")
        pi.image = new_img
        pi.save()

        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(pi.image.path))

    def test_certification_update_replaces_old_image(self):
        cert_img = _make_image()
        cert = Certification.objects.create(
            name="Cert",
            issuing_organization="Org",
            issue_date="2024-01-01",
            image=cert_img,
        )
        old_path = cert.image.path
        self.assertTrue(os.path.exists(old_path))

        new_img = _make_image(name="new_cert.png")
        cert.image = new_img
        cert.save()

        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(cert.image.path))

    def test_achievement_update_replaces_old_image(self):
        ach_img = _make_image()
        ach = Achievement.objects.create(title="Ach", description="desc", date="2024-01-01", image=ach_img)
        old_path = ach.image.path
        self.assertTrue(os.path.exists(old_path))

        new_img = _make_image(name="new_ach.png")
        ach.image = new_img
        ach.save()

        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(ach.image.path))

    def test_experience_photo_update_replaces_old_image(self):
        exp = Experience.objects.create(company_name="Corp", start_date="2024-01-01")
        photo_img = _make_image()
        photo = ExperiencePhoto.objects.create(experience=exp, image=photo_img)
        old_path = photo.image.path
        self.assertTrue(os.path.exists(old_path))

        new_img = _make_image(name="new_exp_photo.png")
        photo.image = new_img
        photo.save()

        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(photo.image.path))

    def test_resume_update_replaces_old_file(self):
        resume1 = SimpleUploadedFile("resume1.pdf", b"pdf1", content_type="application/pdf")
        resume = Resume.objects.create(title="Resume", pdf_file=resume1)
        old_path = resume.pdf_file.path
        self.assertTrue(os.path.exists(old_path))

        resume2 = SimpleUploadedFile("resume2.pdf", b"pdf2", content_type="application/pdf")
        resume.pdf_file = resume2
        resume.save()

        self.assertFalse(os.path.exists(old_path))
        self.assertTrue(os.path.exists(resume.pdf_file.path))
