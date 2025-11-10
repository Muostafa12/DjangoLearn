"""
Task models for the taskmaster application.
Demonstrates complex relationships, model inheritance, and custom managers.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import markdown


class TaskManager(models.Manager):
    """Custom manager for Task model with useful querysets"""

    def active(self):
        """Return only active tasks (not completed or cancelled)"""
        return self.exclude(status__in=['completed', 'cancelled'])

    def high_priority(self):
        """Return high priority tasks"""
        return self.filter(priority='high')

    def overdue(self):
        """Return overdue tasks"""
        from django.utils import timezone
        return self.filter(
            due_date__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        )

    def for_user(self, user):
        """Return tasks assigned to a specific user"""
        return self.filter(assignees=user)


class Task(models.Model):
    """
    Task model for managing individual tasks within projects.
    Demonstrates choices, validators, and complex relationships.
    """
    STATUS_CHOICES = [
        ('todo', _('To Do')),
        ('in_progress', _('In Progress')),
        ('review', _('In Review')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]

    # Basic info
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo'
    )
    priority = models.CharField(
        _('priority'),
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    # Relationships
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name=_('project')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name=_('created by')
    )
    assignees = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_tasks',
        blank=True,
        verbose_name=_('assignees')
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name=_('parent task')
    )

    # Progress tracking
    estimated_hours = models.DecimalField(
        _('estimated hours'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    actual_hours = models.DecimalField(
        _('actual hours'),
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    completion_percentage = models.IntegerField(
        _('completion percentage'),
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Dates
    due_date = models.DateTimeField(_('due date'), null=True, blank=True)
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = TaskManager()

    class Meta:
        db_table = 'tasks'
        verbose_name = _('task')
        verbose_name_plural = _('tasks')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.due_date:
            return False
        from django.utils import timezone
        return self.due_date < timezone.now() and self.status not in ['completed', 'cancelled']

    @property
    def description_html(self):
        """Convert markdown description to HTML"""
        return markdown.markdown(self.description)

    @property
    def subtask_count(self):
        """Get number of subtasks"""
        return self.subtasks.count()

    @property
    def completed_subtask_count(self):
        """Get number of completed subtasks"""
        return self.subtasks.filter(status='completed').count()

    def assign_to(self, user):
        """Assign task to a user"""
        self.assignees.add(user)

    def unassign_from(self, user):
        """Unassign task from a user"""
        self.assignees.remove(user)

    def mark_as_completed(self):
        """Mark task as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.completion_percentage = 100
        self.save()

    def mark_as_in_progress(self):
        """Mark task as in progress"""
        from django.utils import timezone
        if not self.started_at:
            self.started_at = timezone.now()
        self.status = 'in_progress'
        self.save()


class Comment(models.Model):
    """
    Comment model for task discussions.
    Demonstrates nested comments and text content.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('task')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('author')
    )
    content = models.TextField(_('content'))
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('parent comment')
    )

    # Metadata
    is_edited = models.BooleanField(_('is edited'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.author.email} on {self.task.title}"

    @property
    def content_html(self):
        """Convert markdown content to HTML"""
        return markdown.markdown(self.content)

    @property
    def reply_count(self):
        """Get number of replies"""
        return self.replies.count()


class TaskAttachment(models.Model):
    """
    Model for task file attachments.
    Demonstrates file uploads and file handling.
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('task')
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_attachments',
        verbose_name=_('uploaded by')
    )
    file = models.FileField(
        _('file'),
        upload_to='task_attachments/%Y/%m/%d/'
    )
    filename = models.CharField(_('filename'), max_length=255)
    file_size = models.IntegerField(_('file size'), help_text=_('Size in bytes'))
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_attachments'
        verbose_name = _('task attachment')
        verbose_name_plural = _('task attachments')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} - {self.task.title}"

    def save(self, *args, **kwargs):
        """Override save to set filename and file_size"""
        if self.file:
            self.filename = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_size_kb(self):
        """Get file size in KB"""
        return round(self.file_size / 1024, 2)

    @property
    def file_size_mb(self):
        """Get file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
