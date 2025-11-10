"""
Signals for the tasks app.
Demonstrates using signals for automatic notifications.
"""

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Task, Comment


@receiver(post_save, sender=Task)
def task_created_or_updated(sender, instance, created, **kwargs):
    """
    Send notification when a task is created or updated.
    This will be handled by Celery for async processing.
    """
    from taskmaster.notifications.tasks import send_task_notification

    if created:
        # Task was just created
        send_task_notification.delay(
            task_id=instance.id,
            notification_type='task_created'
        )
    else:
        # Task was updated
        send_task_notification.delay(
            task_id=instance.id,
            notification_type='task_updated'
        )


@receiver(m2m_changed, sender=Task.assignees.through)
def task_assignee_changed(sender, instance, action, pk_set, **kwargs):
    """
    Send notification when a user is assigned to a task.
    """
    from taskmaster.notifications.tasks import send_task_assignment_notification

    if action == 'post_add':
        # Users were added as assignees
        for user_id in pk_set:
            send_task_assignment_notification.delay(
                task_id=instance.id,
                user_id=user_id
            )


@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    """
    Send notification when a comment is created on a task.
    """
    from taskmaster.notifications.tasks import send_comment_notification

    if created:
        send_comment_notification.delay(
            comment_id=instance.id
        )
