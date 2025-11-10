"""
Views for the notifications app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Notification model.
    Read-only as notifications are created by the system.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get notifications for current user"""
        queryset = Notification.objects.filter(
            recipient=self.request.user
        ).select_related('sender')

        # Filter by read status
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)

        # Filter by type
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)

        return queryset

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark notification as read.
        Endpoint: /api/notifications/{id}/mark_as_read/
        """
        notification = self.get_object()
        notification.mark_as_read()

        return Response({
            'message': 'Notification marked as read',
            'notification': NotificationSerializer(notification).data
        })

    @action(detail=True, methods=['post'])
    def mark_as_unread(self, request, pk=None):
        """
        Mark notification as unread.
        Endpoint: /api/notifications/{id}/mark_as_unread/
        """
        notification = self.get_object()
        notification.mark_as_unread()

        return Response({
            'message': 'Notification marked as unread',
            'notification': NotificationSerializer(notification).data
        })

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """
        Mark all notifications as read.
        Endpoint: /api/notifications/mark_all_as_read/
        """
        from django.utils import timezone

        updated = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        return Response({
            'message': f'{updated} notifications marked as read'
        })

    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications.
        Endpoint: /api/notifications/unread_count/
        """
        count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()

        return Response({'unread_count': count})
