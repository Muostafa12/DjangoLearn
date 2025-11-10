"""
Serializers for the notifications app.
"""

from rest_framework import serializers
from .models import Notification
from taskmaster.accounts.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'sender', 'notification_type',
            'title', 'message', 'is_read', 'read_at',
            'content_type', 'object_id', 'created_at'
        ]
        read_only_fields = ['id', 'recipient', 'sender', 'created_at', 'read_at']
