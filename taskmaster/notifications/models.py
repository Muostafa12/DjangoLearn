"""
Notification models for the taskmaster application.
Demonstrates notifications system and polymorphic relationships.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class NotificationManager(models.Manager):
    """Custom manager for Notification model"""

    def unread(self):
        """Return unread notifications"""
        return self.filter(is_read=False)

    def read(self):
        """Return read notifications"""
        return self.filter(is_read=True)

    def for_user(self, user):
        """Return notifications for a specific user"""
        return self.filter(recipient=user)


class Notification(models.Model):
    """
    Notification model for user notifications.
    Demonstrates GenericForeignKey for polymorphic relationships.
    """
    NOTIFICATION_TYPES = [
        ('task_created', _('Task Created')),
        ('task_updated', _('Task Updated')),
        ('task_assigned', _('Task Assigned')),
        ('task_completed', _('Task Completed')),
        ('task_overdue', _('Task Overdue')),
        ('comment_added', _('Comment Added')),
        ('comment_reply', _('Comment Reply')),
        ('project_invitation', _('Project Invitation')),
        ('mention', _('Mention')),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('recipient')
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sent_notifications',
        verbose_name=_('sender')
    )

    notification_type = models.CharField(
        _('notification type'),
        max_length=50,
        choices=NOTIFICATION_TYPES
    )
    title = models.CharField(_('title'), max_length=255)
    message = models.TextField(_('message'))

    # Generic relation to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Status
    is_read = models.BooleanField(_('is read'), default=False)
    read_at = models.DateTimeField(_('read at'), null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    objects = NotificationManager()

    class Meta:
        db_table = 'notifications'
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.email}"

    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save()
