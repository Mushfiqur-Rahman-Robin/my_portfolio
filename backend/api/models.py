import uuid

from django.db import models


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Changed to UUID
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(
        upload_to="projects/banners/",
        help_text="Main image for project preview/banner",
    )  # Renamed to clarify purpose
    project_url = models.URLField(blank=True, null=True)
    repo_url = models.URLField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="projects", blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False, help_text="Select to show on homepage featured section")  # New field
    code_snippet = models.TextField(blank=True, null=True, help_text="Code snippet for syntax highlighting")  # New field for code
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title


# New model for additional project images (gallery)
class ProjectImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, related_name="gallery_images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]
        verbose_name = "Project Gallery Image"
        verbose_name_plural = "Project Gallery Images"

    def __str__(self):
        return f"{self.project.title} - {self.caption or self.image.name}"


class Publication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    authors = models.CharField(max_length=500)
    conference = models.CharField(max_length=300)
    publication_url = models.URLField()
    published_date = models.DateField()
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-published_date"]
        verbose_name = "Publication"
        verbose_name_plural = "Publications"

    def __str__(self):
        return self.title


class Certification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    credential_url = models.URLField(blank=True, null=True)
    issue_date = models.DateField()
    image = models.ImageField(upload_to="certifications/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-issue_date"]
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"

    def __str__(self):
        return self.name


class Achievement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    image = models.ImageField(upload_to="achievements/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "-date"]
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"

    def __str__(self):
        return f"Message from {self.name} ({self.email})"


class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to="resumes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Resume"
        verbose_name_plural = "Resumes"

    def __str__(self):
        return self.title


class VisitorCount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Changed to UUID for consistency
    count = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Visitor Count"
        verbose_name_plural = "Visitor Counts"

    def __str__(self):
        return f"Total Visitors: {self.count}"


class Experience(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200, blank=True)  # Added for resume content
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    work_details = models.TextField(help_text="Detailed description of responsibilities and achievements")
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["display_order", "-start_date"]
        verbose_name = "Professional Experience"
        verbose_name_plural = "Professional Experiences"

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class ExperiencePhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experience = models.ForeignKey(Experience, related_name="photos", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="experience/memories/")
    caption = models.CharField(max_length=255, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]
        verbose_name = "Experience Photo"
        verbose_name_plural = "Experience Photos"

    def __str__(self):
        return f"Photo for {self.experience.company_name} - {self.caption or self.image.name}"


class ChatSession(models.Model):
    """Represents a single, unique chat conversation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"

    def __str__(self):
        return f"Chat Session {self.id} on {self.created_at.strftime('%Y-%m-%d')}"


class ChatMessage(models.Model):
    """Represents a single message within a chat session."""

    SENDER_CHOICES = (
        ("user", "User"),
        ("bot", "Bot"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, related_name="messages", on_delete=models.CASCADE)
    sender = models.CharField(max_length=4, choices=SENDER_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return f"{self.get_sender_display()} message at {self.created_at.strftime('%H:%M')}"
