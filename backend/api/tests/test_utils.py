from io import BytesIO
from unittest.mock import MagicMock, patch

from django.test import TestCase

from ..utils import clean_html, convert_image_to_webp, extract_pdf_text


class CleanHtmlTests(TestCase):
    def test_plain_text_unchanged(self):
        result = clean_html("Hello world")
        self.assertEqual(result, "Hello world")

    def test_removes_script_tags(self):
        result = clean_html("<p>Hi</p><script>alert('x')</script>")
        self.assertNotIn("alert", result)
        self.assertIn("Hi", result)

    def test_removes_style_tags(self):
        result = clean_html("<p>Hi</p><style>body{color:red}</style>")
        self.assertNotIn("body", result)
        self.assertIn("Hi", result)

    def test_strips_html_tags(self):
        result = clean_html("<p>Hello <b>World</b></p>")
        self.assertEqual(result, "Hello World")

    def test_empty_html(self):
        result = clean_html("<p></p>")
        self.assertEqual(result, "")

    def test_multiline_html(self):
        result = clean_html("<div>Line 1</div><div>Line 2</div>")
        self.assertIn("Line 1", result)
        self.assertIn("Line 2", result)

    def test_collapses_whitespace(self):
        result = clean_html("<p>  spaced  out  </p>")
        self.assertIn("spaced", result)
        self.assertIn("out", result)
        self.assertFalse(any(line == "" for line in result.splitlines() if line))


class ExtractPdfTextTests(TestCase):
    @patch("api.utils.pypdf.PdfReader")
    def test_extracts_text_from_pdf(self, mock_reader):
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Page content"
        mock_reader.return_value.pages = [mock_page]

        result = extract_pdf_text("/fake/path.pdf")
        self.assertEqual(result, "Page content")

    @patch("api.utils.pypdf.PdfReader")
    def test_returns_empty_on_error(self, mock_reader):
        mock_reader.side_effect = Exception("Bad PDF")

        result = extract_pdf_text("/bad/path.pdf")
        self.assertEqual(result, "")

    @patch("api.utils.pypdf.PdfReader")
    def test_skips_empty_pages(self, mock_reader):
        page1 = MagicMock()
        page1.extract_text.return_value = "Content 1"
        page2 = MagicMock()
        page2.extract_text.return_value = ""
        page3 = MagicMock()
        page3.extract_text.return_value = None
        mock_reader.return_value.pages = [page1, page2, page3]

        result = extract_pdf_text("/fake/path.pdf")
        self.assertEqual(result, "Content 1")


class ConvertImageToWebPTests(TestCase):
    def test_raises_error_for_non_image(self):
        fake_file = BytesIO(b"not an image")
        fake_file.name = "test.png"
        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded = SimpleUploadedFile("test.png", fake_file.read(), content_type="image/png")
        with self.assertRaises(ValueError):
            convert_image_to_webp(uploaded)

    def test_converts_png_to_webp(self):
        from PIL import Image

        buf = BytesIO()
        img = Image.new("RGB", (10, 10), color=(255, 0, 0))
        img.save(buf, "png")
        buf.name = "test.png"
        buf.seek(0)

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded = SimpleUploadedFile("test.png", buf.read(), content_type="image/png")

        result = convert_image_to_webp(uploaded)
        self.assertTrue(result.name.endswith(".webp"))
        self.assertGreater(result.size, 0)

    def test_converts_jpg_to_webp(self):
        from PIL import Image

        buf = BytesIO()
        img = Image.new("RGB", (10, 10), color=(0, 255, 0))
        img.save(buf, "jpeg")
        buf.name = "test.jpg"
        buf.seek(0)

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded = SimpleUploadedFile("test.jpg", buf.read(), content_type="image/jpeg")

        result = convert_image_to_webp(uploaded)
        self.assertTrue(result.name.endswith(".webp"))
        self.assertGreater(result.size, 0)

    def test_handles_rgba_image(self):
        from PIL import Image

        buf = BytesIO()
        img = Image.new("RGBA", (10, 10), color=(255, 0, 0, 128))
        img.save(buf, "png")
        buf.name = "test_rgba.png"
        buf.seek(0)

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded = SimpleUploadedFile("test_rgba.png", buf.read(), content_type="image/png")

        result = convert_image_to_webp(uploaded)
        self.assertTrue(result.name.endswith(".webp"))

    def test_filename_without_extension(self):
        from PIL import Image

        buf = BytesIO()
        img = Image.new("RGB", (10, 10), color=(0, 0, 255))
        img.save(buf, "png")
        buf.name = "noext"
        buf.seek(0)

        from django.core.files.uploadedfile import SimpleUploadedFile

        uploaded = SimpleUploadedFile("noext", buf.read(), content_type="image/png")

        result = convert_image_to_webp(uploaded)
        self.assertTrue(result.name.endswith(".webp"))
