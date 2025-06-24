# api/tests.py
import os
import shutil  # Import shutil for directory removal
from io import BytesIO

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from .models import Achievement, Certification, Experience, Project, Publication, Tag

# Define the temporary media root path
# This should be outside the TestCase class definition but can use settings.BASE_DIR
TEST_MEDIA_ROOT = os.path.join(settings.BASE_DIR, "test_media")


def generate_photo_file():
    file = BytesIO()
    image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
    image.save(file, "png")
    file.name = "test_image.png"
    file.seek(0)
    return SimpleUploadedFile(file.name, file.read(), content_type="image/png")


# Apply the override for MEDIA_ROOT to the entire test class
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class APITests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure the test media directory exists before tests run
        os.makedirs(TEST_MEDIA_ROOT, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Clean up the test media directory after all tests in the class have run
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)

    def setUp(self):
        self.client = APIClient()
        self.tag = Tag.objects.create(name="Test Tag")

        # This setup is for objects that already exist before each test runs.
        # The image is created in memory and saved to the test database.
        self.project = Project.objects.create(
            title="Test Project",
            description="A test project",
            image=generate_photo_file(),
            display_order=1,
        )
        self.project.tags.add(self.tag)

        self.publication = Publication.objects.create(
            title="Test Publication",
            authors="John Doe",
            conference="TestConf",
            publication_url="https://example.com",
            published_date="2025-01-01",
            display_order=1,
        )
        self.certification = Certification.objects.create(
            name="Test Certification",
            issuing_organization="Test Org",
            credential_url="https://example.com",
            issue_date="2025-01-01",
            display_order=1,
        )
        self.achievement = Achievement.objects.create(
            title="Test Achievement",
            description="A test achievement",
            date="2025-01-01",
            display_order=1,
        )
        self.experience = Experience.objects.create(
            company_name="Test Company",
            job_title="Test Engineer",
            start_date="2024-01-01",
            end_date="2025-01-01",
            is_current=False,
            work_details="Test details",
            display_order=1,
        )

    def test_get_projects(self):
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Project")

    def test_create_project(self):
        """
        Test creating a project with an image upload.
        This requires using format='multipart' instead of 'json'.
        """
        new_project_data = {
            "title": "New Project",
            "description": "Another test project",
            "image": generate_photo_file(),  # Generate a new file for the upload
            "display_order": 2,
            "tags": [self.tag.name],
        }
        # CRITICAL FIX: Use format='multipart' for file uploads
        response = self.client.post(reverse("project-list"), new_project_data, format="multipart")

        # Check the response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(response.data["title"], "New Project")

    def test_update_project(self):
        url = reverse("project-detail", args=[self.project.id])
        updated_data = {"title": "Updated Project"}
        # PATCHing a simple field can still use 'json' format
        response = self.client.patch(url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Updated Project")

    def test_delete_project(self):
        url = reverse("project-detail", args=[self.project.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Project.objects.count(), 0)

    def test_get_publications(self):
        response = self.client.get(reverse("publication-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Publication")

    def test_get_certifications(self):
        response = self.client.get(reverse("certification-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["name"], "Test Certification")

    def test_get_achievements(self):
        response = self.client.get(reverse("achievement-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Test Achievement")

    def test_create_tag_not_allowed(self):
        """
        Tags are read-only from the API, so POST should be disallowed.
        """
        url = reverse("tag-list")
        tag_data = {"name": "New Tag"}
        response = self.client.post(url, tag_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_experiences(self):
        response = self.client.get(reverse("experience-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["company_name"], "Test Company")
