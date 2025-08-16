# backend/api/signals.py

import os

from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from .chromadb_utils import add_or_update_node, delete_node
from .models import Achievement, Certification, Experience, ExperiencePhoto, Project, ProjectImage, Publication, Resume
from .utils import clean_html, extract_pdf_text  # ADDED clean_html import


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


# --- Existing ChromaDB Signal Handlers ---


@receiver(post_save, sender=Project)
def sync_project_chroma(sender, instance, **kwargs):
    # Apply clean_html to project description (it's RichTextUploadingField, storing HTML)
    cleaned_description = clean_html(instance.description)  # ADDED clean_html
    content = f"Project Title: {instance.title}\nDescription: {cleaned_description}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, url_path="projects"))


@receiver(post_delete, sender=Project)
def delete_project_chroma(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Resume)
def sync_resume_chroma(sender, instance, **kwargs):
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
def delete_resume_chroma(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Certification)
def sync_certification_chroma(sender, instance, **kwargs):
    content = f"Certification: {instance.name}\nIssued by: {instance.issuing_organization}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, title_field="name", url_path="certifications"))


@receiver(post_delete, sender=Certification)
def delete_certification_chroma(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Publication)
def sync_publication_chroma(sender, instance, **kwargs):
    content = f"Publication: {instance.title}\nAuthors: {instance.authors}\nConference: {instance.conference}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, url_path="publications"))


@receiver(post_delete, sender=Publication)
def delete_publication_chroma(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Achievement)
def sync_achievement_chroma(sender, instance, **kwargs):
    content = f"Achievement: {instance.title}\nDescription: {instance.description}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, url_path="achievements"))


@receiver(post_delete, sender=Achievement)
def delete_achievement_chroma(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


@receiver(post_save, sender=Experience)
def sync_experience_chroma(sender, instance, **kwargs):
    # Apply clean_html to experience work_details (which now stores HTML from CKEditor)
    cleaned_work_details = clean_html(instance.work_details)  # ADDED clean_html
    content = f"Experience at {instance.company_name} as {instance.job_title}\nDetails: {cleaned_work_details}"
    add_or_update_node(get_doc_id(instance), content, get_metadata(instance, title_field="company_name", url_path="experience"))


@receiver(post_delete, sender=Experience)
def delete_experience_chroma(sender, instance, **kwargs):
    delete_node(get_doc_id(instance))


# ============================================================================
# FILE DELETION SIGNALS (NO CHANGE NEEDED HERE, ALREADY HANDLED)
# ============================================================================


def delete_file_if_exists(file_field):
    """
    Helper function to safely delete a file from the filesystem if it exists.

    Args:
        file_field: Django FileField or ImageField instance (e.g., instance.image)
    """
    if file_field and hasattr(file_field, "path"):
        try:
            if os.path.isfile(file_field.path):
                os.remove(file_field.path)
                print(f"DEBUG: Successfully deleted file: {file_field.path}")
            else:
                print(f"DEBUG: File not found at path: {file_field.path}")
        except (OSError, ValueError) as e:
            # ValueError can occur if the file field is empty/invalid before saving
            # OSError can occur if file doesn't exist or permission issues
            print(f"ERROR: Failed to delete file {file_field.name} from path {file_field.path if hasattr(file_field, 'path') else 'N/A'}: {e}")


# --- Project File Deletion ---
@receiver(post_delete, sender=Project)
def delete_project_main_image(sender, instance, **kwargs):
    """Delete the main project image when a Project is deleted."""
    delete_file_if_exists(instance.image)


@receiver(post_delete, sender=ProjectImage)
def delete_project_gallery_image(sender, instance, **kwargs):
    """Delete gallery images when a ProjectImage is deleted."""
    delete_file_if_exists(instance.image)


# --- Certification Image Deletion ---
@receiver(post_delete, sender=Certification)
def delete_certification_image(sender, instance, **kwargs):
    """Delete certification image when a Certification is deleted."""
    delete_file_if_exists(instance.image)


@receiver(post_delete, sender=Achievement)
def delete_achievement_image(sender, instance, **kwargs):
    """Delete achievement image when an Achievement is deleted."""
    delete_file_if_exists(instance.image)


# --- Experience Photo Deletion ---
@receiver(post_delete, sender=ExperiencePhoto)
def delete_experience_photo(sender, instance, **kwargs):
    """Delete experience photo when an ExperiencePhoto is deleted."""
    delete_file_if_exists(instance.image)


# --- Resume File Deletion ---
@receiver(post_delete, sender=Resume)
def delete_resume_file(sender, instance, **kwargs):
    """Delete resume PDF file when a Resume is deleted."""
    delete_file_if_exists(instance.pdf_file)


# --- On File Update (using pre_save) ---
@receiver(pre_save, sender=Project)
def delete_old_project_image_on_update(sender, instance, **kwargs):
    """Delete the old main image file when a new one is uploaded for Project."""
    if not instance.pk:  # Object is being created, not updated
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.image and old_instance.image.name != instance.image.name:
            delete_file_if_exists(old_instance.image)
    except sender.DoesNotExist:
        pass  # Old instance not found, nothing to delete (shouldn't happen with instance.pk check)


@receiver(pre_save, sender=ProjectImage)
def delete_old_project_gallery_image_on_update(sender, instance, **kwargs):
    """Delete the old gallery image file when a new one is uploaded for ProjectImage."""
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.image and old_instance.image.name != instance.image.name:
            delete_file_if_exists(old_instance.image)
    except sender.DoesNotExist:
        pass


@receiver(pre_save, sender=Certification)
def delete_old_certification_image_on_update(sender, instance, **kwargs):
    """Delete the old image file when a new one is uploaded for Certification."""
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.image and old_instance.image.name != instance.image.name:
            delete_file_if_exists(old_instance.image)
    except sender.DoesNotExist:
        pass


@receiver(pre_save, sender=Achievement)
def delete_old_achievement_image_on_update(sender, instance, **kwargs):
    """Delete the old image file when a new one is uploaded for Achievement."""
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.image and old_instance.image.name != instance.image.name:
            delete_file_if_exists(old_instance.image)
    except sender.DoesNotExist:
        pass


@receiver(pre_save, sender=ExperiencePhoto)
def delete_old_experience_photo_on_update(sender, instance, **kwargs):
    """Delete the old image file when a new one is uploaded for ExperiencePhoto."""
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.image and old_instance.image.name != instance.image.name:
            delete_file_if_exists(old_instance.image)
    except sender.DoesNotExist:
        pass


@receiver(pre_save, sender=Resume)
def delete_old_resume_file_on_update(sender, instance, **kwargs):
    """Delete the old PDF file when a new one is uploaded for Resume."""
    # Special handling for Resume because you typically only want one resume
    # and the ChromaDB signal already handles deleting other resume nodes.
    # This pre_save ensures the *previous file for this specific instance* is deleted
    # if a new one is uploaded.
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.pdf_file and old_instance.pdf_file.name != instance.pdf_file.name:
            delete_file_if_exists(old_instance.pdf_file)
    except sender.DoesNotExist:
        pass
