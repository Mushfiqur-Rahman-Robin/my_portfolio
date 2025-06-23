from rest_framework import serializers

from .models import Achievement, Certification, ContactMessage, Project, Publication, Resume, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ProjectSerializer(serializers.ModelSerializer):
    # Use SlugRelatedField for tags to handle them by name in API
    tags = serializers.SlugRelatedField(many=True, slug_field="name", queryset=Tag.objects.all(), required=True)

    class Meta:
        model = Project
        fields = "__all__"

    # Custom create/update to handle tags properly
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

        if tags_data is not None:  # Only update if tags were provided
            instance.tags.clear()  # Clear existing tags
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
