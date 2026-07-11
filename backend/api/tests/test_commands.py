from io import BytesIO, StringIO
from unittest.mock import MagicMock, patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from PIL import Image

from ..models import Achievement, Certification, Experience, Project, Publication


def _make_image_file():
    buf = BytesIO()
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    img.save(buf, "png")
    buf.name = "test.png"
    buf.seek(0)
    return SimpleUploadedFile(buf.name, buf.read(), content_type="image/png")


class BackfillImagesToWebpTests(TestCase):
    def test_quality_out_of_range_raises_error(self):
        with self.assertRaises(CommandError):
            call_command("backfill_images_to_webp", quality=0)

    def test_quality_above_100_raises_error(self):
        with self.assertRaises(CommandError):
            call_command("backfill_images_to_webp", quality=101)

    def test_delete_old_without_apply_raises_error(self):
        with self.assertRaises(CommandError):
            call_command("backfill_images_to_webp", delete_old=True, apply=False)

    def test_convert_file_obj_to_webp_bytes(self):
        buf = BytesIO()
        img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 128))
        img.save(buf, "png")
        buf.name = "test.png"
        buf.seek(0)

        from ..management.commands.backfill_images_to_webp import convert_file_obj_to_webp_bytes

        result = convert_file_obj_to_webp_bytes(buf, quality=85)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

    @patch("api.management.commands.backfill_images_to_webp.default_storage")
    def test_dry_run_mode_default(self, mock_storage):
        mock_storage.exists.return_value = True
        mock_storage.open.return_value = BytesIO()

        Project.objects.create(title="Test", description="desc", image=_make_image_file())

        out = StringIO()
        call_command("backfill_images_to_webp", stdout=out)
        output = out.getvalue()

        self.assertIn("DRY-RUN", output)

    @patch("api.management.commands.backfill_images_to_webp.default_storage")
    def test_converts_image_with_apply(self, mock_storage):
        mock_storage.exists.return_value = True
        mock_storage.open.return_value = BytesIO()
        mock_storage.save.return_value = "projects/banners/test.webp"

        Project.objects.create(title="Test", description="desc", image=_make_image_file())

        out = StringIO()
        call_command("backfill_images_to_webp", apply=True, stdout=out)
        output = out.getvalue()

        self.assertIn("APPLY", output)

    @patch("api.management.commands.backfill_images_to_webp.default_storage")
    def test_skips_webp_images(self, mock_storage):
        mock_storage.exists.return_value = True

        Project.objects.create(title="Test", description="desc", image=_make_image_file())

        out = StringIO()
        call_command("backfill_images_to_webp", apply=True, stdout=out)
        output = out.getvalue()

        self.assertIn("checked", output)

    @patch("api.management.commands.backfill_images_to_webp.default_storage")
    def test_missing_file_skipped(self, mock_storage):
        mock_storage.exists.return_value = False

        project = Project.objects.create(title="Test", description="desc", image=_make_image_file())
        Project.objects.filter(pk=project.pk).update(image="projects/banners/test.jpg")
        project.refresh_from_db()

        out = StringIO()
        call_command("backfill_images_to_webp", apply=True, stdout=out)
        output = out.getvalue()

        self.assertIn("Missing file", output)


class IndexContentCommandTests(TestCase):
    def setUp(self):
        self.image = _make_image_file()

    @patch("api.management.commands.index_content.get_collection")
    @patch("api.management.commands.index_content.add_or_update_node")
    def test_index_content_without_reindex(self, mock_add, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        out = StringIO()
        call_command("index_content", stdout=out)
        output = out.getvalue()

        self.assertIn("Indexing static content", output)
        self.assertIn("Indexed 'About Me' content", output)
        self.assertIn("Indexed 'Skills' content", output)
        self.assertIn("Indexed 'Contact' content", output)
        self.assertTrue(output.strip().endswith("Content indexing complete!"))

        mock_collection.delete.assert_not_called()
        self.assertGreaterEqual(mock_add.call_count, 3)

    @patch("api.management.commands.index_content.get_collection")
    @patch("api.management.commands.index_content.add_or_update_node")
    def test_index_content_with_reindex(self, mock_add, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.get.return_value = {"ids": ["doc1", "doc2"]}
        mock_get_collection.return_value = mock_collection

        out = StringIO()
        call_command("index_content", reindex=True, stdout=out)
        output = out.getvalue()

        self.assertIn("Clearing existing collection", output)
        mock_collection.delete.assert_called_once_with(ids=["doc1", "doc2"])

    @patch("api.management.commands.index_content.get_collection")
    @patch("api.management.commands.index_content.add_or_update_node")
    def test_index_content_with_empty_collection_reindex(self, mock_add, mock_get_collection):
        mock_collection = MagicMock()
        mock_collection.get.return_value = {"ids": []}
        mock_get_collection.return_value = mock_collection

        out = StringIO()
        call_command("index_content", reindex=True, stdout=out)
        output = out.getvalue()

        self.assertIn("Clearing existing collection", output)

    @patch("api.management.commands.index_content.get_collection")
    @patch("api.management.commands.index_content.add_or_update_node")
    def test_index_content_with_dynamic_data(self, mock_add, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        Project.objects.create(title="Test Project", description="<p>desc</p>", image=self.image)
        Certification.objects.create(name="Test Cert", issuing_organization="Org", issue_date="2024-01-01")
        Publication.objects.create(
            title="Test Pub",
            authors="Author",
            conference="Conf",
            publication_url="https://example.com",
            published_date="2024-01-01",
        )
        Achievement.objects.create(title="Test Ach", description="desc", date="2024-01-01")
        Experience.objects.create(
            company_name="Test Corp",
            job_title="Engineer",
            start_date="2024-01-01",
            work_details="<p>details</p>",
        )

        out = StringIO()
        call_command("index_content", stdout=out)
        output = out.getvalue()

        self.assertIn("Indexed 1 projects", output)
        self.assertIn("Indexed 1 certifications", output)
        self.assertIn("Indexed 1 publications", output)
        self.assertIn("Indexed 1 achievements", output)
        self.assertIn("Indexed 1 experiences", output)

    @patch("api.management.commands.index_content.get_collection")
    @patch("api.management.commands.index_content.add_or_update_node")
    def test_index_content_reports_zero_dynamic(self, mock_add, mock_get_collection):
        mock_collection = MagicMock()
        mock_get_collection.return_value = mock_collection

        out = StringIO()
        call_command("index_content", stdout=out)
        output = out.getvalue()

        self.assertIn("Indexed 0 projects", output)
        self.assertIn("No resume found", output)
