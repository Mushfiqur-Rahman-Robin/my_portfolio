# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Achievement, Certification, Project, Publication


class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.project = Project.objects.create(
            title="Test Project",
            description="A test project",
            image="projects/test.jpg",
            tags="test,python",
            display_order=1,
        )
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

    def test_get_projects(self):
        response = self.client.get(reverse("project-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Project")

    def test_get_publications(self):
        response = self.client.get(reverse("publication-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Publication")

    def test_get_certifications(self):
        response = self.client.get(reverse("certification-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Certification")

    def test_get_achievements(self):
        response = self.client.get(reverse("achievement-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Achievement")
