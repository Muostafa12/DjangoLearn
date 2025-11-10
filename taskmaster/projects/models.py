"""
Project models for the taskmaster application.
Demonstrates many-to-many relationships, choices, and model methods.
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Project(models.Model):
    """
    Project model for organizing tasks.
    Demonstrates model choices and timestamps.
    """
    STATUS_CHOICES = [
        ('planning', _('Planning')),
        ('active', _('Active')),
        ('on_hold', _('On Hold')),
        ('completed', _('Completed')),
        ('archived', _('Archived')),
    ]

    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='planning'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        verbose_name=_('owner')
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectMember',
        related_name='projects',
        verbose_name=_('members')
    )

    # Dates
    start_date = models.DateField(_('start date'), null=True, blank=True)
    end_date = models.DateField(_('end date'), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        verbose_name = _('project')
        verbose_name_plural = _('projects')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['owner', '-created_at']),
        ]

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        """Check if project is active"""
        return self.status == 'active'

    @property
    def task_count(self):
        """Get total number of tasks"""
        return self.tasks.count()

    @property
    def completed_task_count(self):
        """Get number of completed tasks"""
        return self.tasks.filter(status='completed').count()

    @property
    def completion_percentage(self):
        """Calculate project completion percentage"""
        total = self.task_count
        if total == 0:
            return 0
        return round((self.completed_task_count / total) * 100, 2)


class ProjectMember(models.Model):
    """
    Through model for Project-User relationship.
    Demonstrates custom through model for many-to-many relationships.
    """
    ROLE_CHOICES = [
        ('owner', _('Owner')),
        ('admin', _('Admin')),
        ('member', _('Member')),
        ('viewer', _('Viewer')),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships'
    )
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='member'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'project_members'
        verbose_name = _('project member')
        verbose_name_plural = _('project members')
        unique_together = ['project', 'user']
        ordering = ['project', '-joined_at']

    def __str__(self):
        return f"{self.user.email} - {self.project.name} ({self.role})"

    @property
    def can_manage_project(self):
        """Check if member can manage project"""
        return self.role in ['owner', 'admin']
