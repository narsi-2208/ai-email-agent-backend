from rest_framework import serializers
from .models import EmailMessage

class EmailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailMessage
        fields = [
            "id",
            "gmail_id",
            "thread_id",
            "sender",
            "recipient",
            "subject",
            "snippet",
            "body",
            "labels",
            "internal_date",
            "fetched_at",
        ]

class DraftSerializer(serializers.Serializer):
    id = serializers.CharField()
    threadId = serializers.CharField()
    subject = serializers.CharField()
    snippet = serializers.CharField()
    body = serializers.CharField()