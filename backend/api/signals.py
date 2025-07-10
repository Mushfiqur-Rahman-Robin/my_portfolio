# backend/api/signals.py

import os

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .chromadb_utils import add_or_update_node, delete_node
from .models import Achievement, Certification, Experience, Project, Publication, Resume
from .utils import extract_pdf_text


def get_doc_id(instance):
    """Generates a unique document ID for a model instance."""
    return f"{instance.__class__.__name__.lower()}-{instance.id}"


def get_metadata(instance, title_field="title", url_path=None):
    """Generates metadata for a model instance."""
    title = getattr(instance, title_field, None) or getattr(instance, "name", "Untitled")
    return {
        "type": instance.__class__.__name__.lower(),
        "title": str(title),
        "id": str(instance.id),
        "url": f"/{url_path}/{instance.id}/" if url_path else "",
    }


# --- Signal Handlers ---


@receiver(post_save, sender=Project)
def sync_project(sender, instance, **kwargs):
    content = f"Project Title: {instance.title}\nDescription: {instance.description}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, url_path="projects"))


@receiver(post_delete, sender=Project)
def delete_project(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Resume)
def sync_resume(sender, instance, **kwargs):
    # Delete all other resume nodes to ensure only the latest one is indexed
    other_resumes = Resume.objects.exclude(pk=instance.pk)
    for old_resume in other_resumes:
        delete_node(get_doc_id(old_resume))

    # Index the new/updated resume
    pdf_path = os.path.join(settings.MEDIA_ROOT, instance.pdf_file.name)
    if os.path.exists(pdf_path):
        content = extract_pdf_text(pdf_path)
        if content:
            add_or_update_node(get_doc_id(instance), content, get_metadata(instance, url_path="resume"))


@receiver(post_delete, sender=Resume)
def delete_resume(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Certification)
def sync_certification(sender, instance, **kwargs):
    content = f"Certification: {instance.name}\nIssued by: {instance.issuing_organization}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, title_field="name", url_path="certifications"))


@receiver(post_delete, sender=Certification)
def delete_certification(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Publication)
def sync_publication(sender, instance, **kwargs):
    content = f"Publication: {instance.title}\nAuthors: {instance.authors}\nConference: {instance.conference}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, url_path="publications"))


@receiver(post_delete, sender=Publication)
def delete_publication(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Achievement)
def sync_achievement(sender, instance, **kwargs):
    content = f"Achievement: {instance.title}\nDescription: {instance.description}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, url_path="achievements"))


@receiver(post_delete, sender=Achievement)
def delete_achievement(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Experience)
def sync_experience(sender, instance, **kwargs):
    content = f"Experience at {instance.company_name} as {instance.job_title}\nDetails: {instance.work_details}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, title_field="company_name", url_path="experience"))


@receiver(post_delete, sender=Experience)
def delete_experience(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))
