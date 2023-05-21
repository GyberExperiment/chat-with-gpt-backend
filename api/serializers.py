from rest_framework import serializers


class AssistantSerializer(serializers.Serializer): # noqa
    user_id = serializers.IntegerField()
    chat_id = serializers.IntegerField()
    content = serializers.CharField()
