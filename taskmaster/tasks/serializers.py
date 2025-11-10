"""
Serializers for the tasks app.
"""

from rest_framework import serializers
from .models import Task, Comment, TaskAttachment
from taskmaster.accounts.serializers import UserSerializer


class TaskAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for TaskAttachment model"""
    uploaded_by = UserSerializer(read_only=True)
    file_size_kb = serializers.FloatField(read_only=True)

    class Meta:
        model = TaskAttachment
        fields = ['id', 'file', 'filename', 'file_size', 'file_size_kb', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['id', 'filename', 'file_size', 'uploaded_at']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    author = UserSerializer(read_only=True)
    content_html = serializers.CharField(read_only=True)
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'task', 'author', 'content', 'content_html',
            'parent_comment', 'reply_count', 'is_edited',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'is_edited', 'created_at', 'updated_at']


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer for Task list view"""
    created_by = UserSerializer(read_only=True)
    assignees = UserSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'priority', 'project', 'project_name',
            'created_by', 'assignees', 'due_date', 'is_overdue',
            'completion_percentage', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer for Task detail view"""
    created_by = UserSerializer(read_only=True)
    assignees = UserSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    attachments = TaskAttachmentSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    description_html = serializers.CharField(read_only=True)
    subtask_count = serializers.IntegerField(read_only=True)
    completed_subtask_count = serializers.IntegerField(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'description_html',
            'status', 'priority', 'project', 'project_name',
            'created_by', 'assignees', 'parent_task',
            'estimated_hours', 'actual_hours', 'completion_percentage',
            'due_date', 'started_at', 'completed_at',
            'is_overdue', 'subtask_count', 'completed_subtask_count',
            'comments', 'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    assignee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority',
            'project', 'parent_task', 'estimated_hours',
            'due_date', 'assignee_ids'
        ]

    def create(self, validated_data):
        """Create task and assign users"""
        assignee_ids = validated_data.pop('assignee_ids', [])
        user = self.context['request'].user

        task = Task.objects.create(created_by=user, **validated_data)

        if assignee_ids:
            task.assignees.set(assignee_ids)

        return task


class TaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating tasks"""
    assignee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'status', 'priority',
            'estimated_hours', 'actual_hours', 'completion_percentage',
            'due_date', 'assignee_ids'
        ]

    def update(self, instance, validated_data):
        """Update task and assignees"""
        assignee_ids = validated_data.pop('assignee_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if assignee_ids is not None:
            instance.assignees.set(assignee_ids)

        return instance
