from rest_framework import serializers

from simple_media_manager.infrastructure.common.serializers.custom_fields.fields import Base64ImageField
from simple_media_manager.infrastructure.models import Image


class ImageInputSerializer(serializers.Serializer):
    image = Base64ImageField(required=False, allow_null=False, allow_empty_file=False)
    name = serializers.CharField(required=False, allow_null=False)
    categories = serializers.ListField(required=True, allow_null=False, child=serializers.IntegerField())


class ImageMultipleInputSerializer(serializers.Serializer):
    image = Base64ImageField(required=False, allow_null=False, allow_empty_file=False)
    name = serializers.CharField(required=False, allow_null=False)


class ImageOutputSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='thumbnail')

    class Meta:
        model = Image
        fields = ('name', 'image', 'thumbnail', 'compact', 'description', 'created_at')


class BriefImageOutputSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(source='thumbnail')

    class Meta:
        model = Image
        fields = ('id', 'image')


class SearchImageInputParameterSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=False)
