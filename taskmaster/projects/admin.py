"""
Admin configuration for the projects app.
"""

from django.contrib import admin
from .models import Project, ProjectMember


class ProjectMemberInline(admin.TabularInline):
    """Inline admin for ProjectMember"""
    model = ProjectMember
    extra = 1
    fields = ('user', 'role', 'joined_at')
    readonly_fields = ('joined_at',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin for Project model"""
    list_display = ('name', 'owner', 'status', 'task_count', 'completion_percentage', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    readonly_fields = ('created_at', 'updated_at', 'task_count', 'completed_task_count', 'completion_percentage')
    inlines = [ProjectMemberInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'status', 'owner')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'created_at', 'updated_at')
        }),
        ('Statistics', {
            'fields': ('task_count', 'completed_task_count', 'completion_percentage')
        }),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """Admin for ProjectMember model"""
    list_display = ('project', 'user', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')
    search_fields = ('project__name', 'user__email')
    readonly_fields = ('joined_at',)
