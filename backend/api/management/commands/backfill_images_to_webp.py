from io import BytesIO
from pathlib import Path, PurePosixPath

from django.apps import apps
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.db import models as django_models
from PIL import Image, UnidentifiedImageError

SUPPORTED_SOURCE_EXTENSIONS = {"jpg", "jpeg", "png"}
SKIP_EXTENSIONS = {"webp", "svg"}


def convert_file_obj_to_webp_bytes(file_obj, quality=85):
    file_obj.seek(0)
    with Image.open(file_obj) as image:
        has_alpha = image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info)
        image = image.convert("RGBA" if has_alpha else "RGB")

        output = BytesIO()
        image.save(output, format="WEBP", quality=quality)
        return output.getvalue()


class Command(BaseCommand):
    help = "One-time backfill: convert existing jpg/jpeg/png ImageField files to webp and update DB paths safely."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply changes. Without this flag, command runs in dry-run mode.",
        )
        parser.add_argument(
            "--delete-old",
            action="store_true",
            help="Delete old jpg/jpeg/png files after successful DB update.",
        )
        parser.add_argument(
            "--quality",
            type=int,
            default=85,
            help="WebP quality (1-100). Default: 85.",
        )

    def handle(self, *args, **options):
        apply_changes = options["apply"]
        delete_old = options["delete_old"]
        quality = options["quality"]

        if quality < 1 or quality > 100:
            raise CommandError("--quality must be between 1 and 100")

        if not apply_changes and delete_old:
            raise CommandError("--delete-old requires --apply")

        mode_label = "APPLY" if apply_changes else "DRY-RUN"
        self.stdout.write(self.style.WARNING(f"Starting image backfill in {mode_label} mode..."))
        self.stdout.write(self.style.WARNING("Back up database and media before running with --apply in production."))

        stats = {
            "checked": 0,
            "empty": 0,
            "unsupported": 0,
            "skipped": 0,
            "missing_file": 0,
            "would_convert": 0,
            "would_repoint": 0,
            "converted": 0,
            "repointed": 0,
            "deleted_old": 0,
            "errors": 0,
        }

        api_models = apps.get_app_config("api").get_models()

        for model in api_models:
            image_fields = [field for field in model._meta.fields if isinstance(field, django_models.ImageField)]
            if not image_fields:
                continue

            self.stdout.write(self.style.NOTICE(f"Processing model: {model.__name__}"))

            for instance in model.objects.iterator():
                for field in image_fields:
                    stats["checked"] += 1

                    image_field_file = getattr(instance, field.name)
                    if not image_field_file:
                        stats["empty"] += 1
                        continue

                    old_name = image_field_file.name
                    if not old_name:
                        stats["empty"] += 1
                        continue

                    extension = Path(old_name).suffix.lower().lstrip(".")

                    if extension in SKIP_EXTENSIONS:
                        stats["skipped"] += 1
                        continue

                    if extension not in SUPPORTED_SOURCE_EXTENSIONS:
                        stats["unsupported"] += 1
                        continue

                    if not default_storage.exists(old_name):
                        stats["missing_file"] += 1
                        self.stdout.write(self.style.WARNING(f"Missing file (skipped): {old_name}"))
                        continue

                    new_name = str(PurePosixPath(old_name).with_suffix(".webp"))

                    if default_storage.exists(new_name):
                        if not apply_changes:
                            stats["would_repoint"] += 1
                            continue

                        model.objects.filter(pk=instance.pk).update(**{field.name: new_name})
                        stats["repointed"] += 1

                        if delete_old and old_name != new_name and default_storage.exists(old_name):
                            default_storage.delete(old_name)
                            stats["deleted_old"] += 1
                        continue

                    if not apply_changes:
                        stats["would_convert"] += 1
                        continue

                    try:
                        with default_storage.open(old_name, "rb") as source_file:
                            webp_bytes = convert_file_obj_to_webp_bytes(source_file, quality=quality)

                        saved_name = default_storage.save(new_name, ContentFile(webp_bytes))

                        model.objects.filter(pk=instance.pk).update(**{field.name: saved_name})
                        stats["converted"] += 1

                        if delete_old and old_name != saved_name and default_storage.exists(old_name):
                            default_storage.delete(old_name)
                            stats["deleted_old"] += 1

                    except (UnidentifiedImageError, OSError, ValueError) as exc:
                        stats["errors"] += 1
                        self.stdout.write(self.style.ERROR(f"Failed to convert {model.__name__}.{field.name} ({instance.pk}): {old_name} ({exc})"))
                    except Exception as exc:
                        stats["errors"] += 1
                        self.stdout.write(self.style.ERROR(f"Unexpected error for {model.__name__}.{field.name} ({instance.pk}): {old_name} ({exc})"))

        self.stdout.write(self.style.SUCCESS("\nBackfill summary:"))
        for key, value in stats.items():
            self.stdout.write(f"- {key}: {value}")

        if not apply_changes:
            self.stdout.write(self.style.WARNING("Dry-run complete. Re-run with --apply to execute changes."))
