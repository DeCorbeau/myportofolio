from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Skill


class ExperienceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    date_range_display = serializers.CharField(read_only=True)
    description_points = serializers.ListField(child=serializers.CharField(), read_only=True)
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    liked_by_names = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id", "title", "organization", "description", "category",
            "category_display", "thumbnail", "thumbnail_image", "thumbnail_url", "started_at", "ended_at",
            "is_ongoing", "date_range_display", "description_points",
            "like_count", "is_liked", "liked_by_names",
        ]
        read_only_fields = ["id"]

    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_organization(self, value):
        return strip_tags(value).strip()

    def validate_description(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Description cannot be empty.")
        return value

    def validate(self, attrs):
        started = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        if started and ended and ended.date() < started:
            raise serializers.ValidationError(
                {"ended_at": "End date cannot be before the start date."}
            )
        return attrs

    def get_like_count(self, obj):
        return len(obj.liked_by.all())

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.liked_by.all()

    def get_liked_by_names(self, obj):
        return ", ".join(user.username for user in obj.liked_by.all())

    def validate_thumbnail_image(self, value):
        if value and value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError("Image must be 2 MB or smaller.")
        return value

    def get_thumbnail_url(self, obj):
        if obj.thumbnail_image:
            return obj.thumbnail_image.url
        return obj.thumbnail or ""    

class SkillSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    proficiency_display = serializers.CharField(source="get_proficiency_display", read_only=True)
    endorse_count = serializers.SerializerMethodField()
    is_endorsed = serializers.SerializerMethodField()
    endorsed_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Skill
        fields = [
            "id", "name", "category", "category_display",
            "proficiency", "proficiency_display", "impact", "context",
            "endorse_count", "is_endorsed", "endorsed_by_names",
        ]
        read_only_fields = ["id"]

    def validate_name(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_impact(self, value):
        return strip_tags(value).strip()

    def validate_context(self, value):
        return strip_tags(value).strip()

    def get_endorse_count(self, obj):
        return len(obj.endorsed_by.all())

    def get_is_endorsed(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.endorsed_by.all()

    def get_endorsed_by_names(self, obj):
        return ", ".join(user.username for user in obj.endorsed_by.all())