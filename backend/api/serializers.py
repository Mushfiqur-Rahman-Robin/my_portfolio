from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import (
    Achievement,
    Certification,
    ContactMessage,
    Experience,
    ExperiencePhoto,
    Project,
    ProjectImage,
    Publication,
    Resume,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ["id", "image", "caption", "display_order"]


class ProjectSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, slug_field="name", queryset=Tag.objects.all(), required=False
    )  # Changed required to False for flexibility
    gallery_images = ProjectImageSerializer(many=True, read_only=True)  # Nested serializer for gallery images

    class Meta:
        model = Project
        fields = "__all__"

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        project = Project.objects.create(**validated_data)
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            project.tags.add(tag)
        return project

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", None)
        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.clear()
            for tag_name in tags_data:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        return instance


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = "__all__"


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = "__all__"


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = "__all__"


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = "__all__"
        read_only_fields = ["sent_at"]


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = "__all__"
        read_only_fields = ["uploaded_at"]


class ExperiencePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperiencePhoto
        fields = ["id", "image", "caption", "display_order"]


class ExperienceSerializer(serializers.ModelSerializer):
    photos = ExperiencePhotoSerializer(many=True, read_only=True)  # Nested serializer for photos

    # Custom field to display 'Present' instead of end_date if is_current is true
    end_date_display = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = "__all__"

    @extend_schema_field(serializers.CharField)
    def get_end_date_display(self, obj):
        if obj.is_current:
            return "Present"
        elif obj.end_date:
            return obj.end_date.strftime("%b. %Y")
        return ""


class VisitorCountPostSerializer(serializers.Serializer):
    # The VisitorCountView doesn't actually take any input in its POST body,
    # it just increments a counter. So we define an empty serializer for its input.
    pass


class VisitorCountResponseSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)
