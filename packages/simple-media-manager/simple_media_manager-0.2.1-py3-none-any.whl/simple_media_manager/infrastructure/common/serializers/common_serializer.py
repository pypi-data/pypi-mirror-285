from rest_framework import serializers


class IdParameterSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True, allow_null=False)
