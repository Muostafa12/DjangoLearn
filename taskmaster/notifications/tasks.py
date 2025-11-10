"""
Celery tasks for the notifications app.
Demonstrates async task processing with Celery.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


@shared_task
def send_task_notification(task_id, notification_type):
    """
    Send notification when a task is created or updated.
    This runs asynchronously via Celery.
    """
    from taskmaster.tasks.models import Task
    from taskmaster.notifications.models import Notification

    try:
        task = Task.objects.select_related('project', 'created_by').get(id=task_id)

        # Determine recipients (project members)
        recipients = task.project.members.exclude(id=task.created_by.id)

        # Create notification for each recipient
        content_type = ContentType.objects.get_for_model(Task)

        for recipient in recipients:
            if notification_type == 'task_created':
                title = f"New task: {task.title}"
                message = f"{task.created_by.full_name} created a new task '{task.title}' in {task.project.name}"
            else:
                title = f"Task updated: {task.title}"
                message = f"Task '{task.title}' in {task.project.name} has been updated"

            notification = Notification.objects.create(
                recipient=recipient,
                sender=task.created_by,
                notification_type=notification_type,
                title=title,
                message=message,
                content_type=content_type,
                object_id=task.id
            )

            # Send email if user has email notifications enabled
            if recipient.profile.email_notifications:
                send_email_notification.delay(notification.id)

        return f"Notifications sent for task {task_id}"

    except Task.DoesNotExist:
        return f"Task {task_id} not found"


@shared_task
def send_task_assignment_notification(task_id, user_id):
    """
    Send notification when a user is assigned to a task.
    """
    from taskmaster.tasks.models import Task
    from taskmaster.accounts.models import User
    from taskmaster.notifications.models import Notification

    try:
        task = Task.objects.select_related('project', 'created_by').get(id=task_id)
        user = User.objects.get(id=user_id)

        content_type = ContentType.objects.get_for_model(Task)

        notification = Notification.objects.create(
            recipient=user,
            sender=task.created_by,
            notification_type='task_assigned',
            title=f"Task assigned: {task.title}",
            message=f"You have been assigned to task '{task.title}' in {task.project.name}",
            content_type=content_type,
            object_id=task.id
        )

        # Send email if user has email notifications enabled
        if user.profile.email_notifications:
            send_email_notification.delay(notification.id)

        return f"Assignment notification sent for task {task_id} to user {user_id}"

    except (Task.DoesNotExist, User.DoesNotExist) as e:
        return f"Error: {str(e)}"


@shared_task
def send_comment_notification(comment_id):
    """
    Send notification when a comment is added to a task.
    """
    from taskmaster.tasks.models import Comment
    from taskmaster.notifications.models import Notification

    try:
        comment = Comment.objects.select_related(
            'task', 'task__project', 'author'
        ).get(id=comment_id)

        # Notify task assignees and the task creator
        recipients = set(comment.task.assignees.all())
        if comment.task.created_by:
            recipients.add(comment.task.created_by)

        # Don't notify the comment author
        recipients.discard(comment.author)

        content_type = ContentType.objects.get_for_model(comment.task.__class__)

        for recipient in recipients:
            notification = Notification.objects.create(
                recipient=recipient,
                sender=comment.author,
                notification_type='comment_added',
                title=f"New comment on: {comment.task.title}",
                message=f"{comment.author.full_name} commented on '{comment.task.title}': {comment.content[:100]}",
                content_type=content_type,
                object_id=comment.task.id
            )

            # Send email if user has email notifications enabled
            if recipient.profile.email_notifications:
                send_email_notification.delay(notification.id)

        return f"Comment notifications sent for comment {comment_id}"

    except Comment.DoesNotExist:
        return f"Comment {comment_id} not found"


@shared_task
def send_email_notification(notification_id):
    """
    Send email for a notification.
    """
    from taskmaster.notifications.models import Notification

    try:
        notification = Notification.objects.select_related(
            'recipient', 'sender'
        ).get(id=notification_id)

        subject = notification.title
        message = notification.message
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [notification.recipient.email]

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True,
        )

        return f"Email sent for notification {notification_id}"

    except Notification.DoesNotExist:
        return f"Notification {notification_id} not found"


@shared_task
def send_daily_task_reminders():
    """
    Periodic task to send daily task reminders.
    This runs via Celery Beat.
    """
    from taskmaster.tasks.models import Task
    from taskmaster.notifications.models import Notification
    from django.utils import timezone
    from datetime import timedelta

    # Get tasks due in the next 24 hours
    tomorrow = timezone.now() + timedelta(days=1)
    upcoming_tasks = Task.objects.filter(
        due_date__lte=tomorrow,
        due_date__gte=timezone.now(),
        status__in=['todo', 'in_progress']
    ).select_related('project').prefetch_related('assignees')

    notification_count = 0
    content_type = ContentType.objects.get_for_model(Task)

    for task in upcoming_tasks:
        for assignee in task.assignees.all():
            notification = Notification.objects.create(
                recipient=assignee,
                notification_type='task_overdue',
                title=f"Task due soon: {task.title}",
                message=f"Task '{task.title}' in {task.project.name} is due soon",
                content_type=content_type,
                object_id=task.id
            )

            if assignee.profile.email_notifications:
                send_email_notification.delay(notification.id)

            notification_count += 1

    return f"Sent {notification_count} task reminders"


@shared_task
def cleanup_old_notifications():
    """
    Periodic task to cleanup old read notifications.
    This runs via Celery Beat.
    """
    from taskmaster.notifications.models import Notification
    from django.utils import timezone
    from datetime import timedelta

    # Delete read notifications older than 30 days
    cutoff_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = Notification.objects.filter(
        is_read=True,
        read_at__lt=cutoff_date
    ).delete()

    return f"Deleted {deleted_count} old notifications"
