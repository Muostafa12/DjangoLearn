"""
Admin configuration for the tasks app.
"""

from django.contrib import admin
from .models import Task, Comment, TaskAttachment


class CommentInline(admin.TabularInline):
    """Inline admin for Comments"""
    model = Comment
    extra = 0
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)


class TaskAttachmentInline(admin.TabularInline):
    """Inline admin for TaskAttachments"""
    model = TaskAttachment
    extra = 0
    fields = ('file', 'uploaded_by', 'file_size_kb', 'uploaded_at')
    readonly_fields = ('file_size_kb', 'uploaded_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin for Task model"""
    list_display = ('title', 'project', 'status', 'priority', 'due_date', 'is_overdue', 'created_at')
    list_filter = ('status', 'priority', 'created_at', 'due_date')
    search_fields = ('title', 'description', 'project__name')
    readonly_fields = ('created_at', 'updated_at', 'is_overdue', 'description_html')
    filter_horizontal = ('assignees',)
    inlines = [CommentInline, TaskAttachmentInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'description_html', 'project', 'parent_task')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'completion_percentage')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assignees')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours', 'due_date', 'is_overdue')
        }),
        ('Dates', {
            'fields': ('started_at', 'completed_at', 'created_at', 'updated_at')
        }),
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for Comment model"""
    list_display = ('task', 'author', 'created_at', 'is_edited')
    list_filter = ('is_edited', 'created_at')
    search_fields = ('content', 'task__title', 'author__email')
    readonly_fields = ('created_at', 'updated_at', 'content_html')


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    """Admin for TaskAttachment model"""
    list_display = ('filename', 'task', 'uploaded_by', 'file_size_kb', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('filename', 'task__title')
    readonly_fields = ('filename', 'file_size', 'file_size_kb', 'file_size_mb', 'uploaded_at')
