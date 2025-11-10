"""
Views for the tasks app.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db.models import Q, Prefetch
from .models import Task, Comment, TaskAttachment
from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
    CommentSerializer,
    TaskAttachmentSerializer
)


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task model.
    Demonstrates filtering, caching, and custom actions.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get tasks with optimized queries.
        Demonstrates filtering and query optimization.
        """
        user = self.request.user
        queryset = Task.objects.select_related(
            'project', 'created_by', 'parent_task'
        ).prefetch_related(
            'assignees',
            'comments__author',
            'attachments'
        )

        # Filter by project
        project_id = self.request.query_params.get('project', None)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        else:
            # Only show tasks from user's projects
            queryset = queryset.filter(
                Q(project__owner=user) | Q(project__members=user)
            ).distinct()

        # Filter by status
        task_status = self.request.query_params.get('status', None)
        if task_status:
            queryset = queryset.filter(status=task_status)

        # Filter by priority
        priority = self.request.query_params.get('priority', None)
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by assignee
        assignee = self.request.query_params.get('assignee', None)
        if assignee:
            if assignee == 'me':
                queryset = queryset.filter(assignees=user)
            else:
                queryset = queryset.filter(assignees__id=assignee)

        # Show only overdue tasks
        overdue = self.request.query_params.get('overdue', None)
        if overdue == 'true':
            queryset = Task.objects.overdue()

        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Retrieve with caching"""
        task_id = kwargs.get('pk')
        cache_key = f'task_{task_id}'

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        cache.set(cache_key, data, 300)

        return Response(data)

    def perform_update(self, serializer):
        """Update and invalidate cache"""
        instance = serializer.save()
        cache_key = f'task_{instance.id}'
        cache.delete(cache_key)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """
        Mark task as completed.
        Endpoint: /api/tasks/{id}/mark_completed/
        """
        task = self.get_object()
        task.mark_as_completed()

        # Invalidate cache
        cache_key = f'task_{task.id}'
        cache.delete(cache_key)

        return Response({
            'message': 'Task marked as completed',
            'task': TaskDetailSerializer(task).data
        })

    @action(detail=True, methods=['post'])
    def mark_in_progress(self, request, pk=None):
        """
        Mark task as in progress.
        Endpoint: /api/tasks/{id}/mark_in_progress/
        """
        task = self.get_object()
        task.mark_as_in_progress()

        # Invalidate cache
        cache_key = f'task_{task.id}'
        cache.delete(cache_key)

        return Response({
            'message': 'Task marked as in progress',
            'task': TaskDetailSerializer(task).data
        })

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Add a comment to the task.
        Endpoint: /api/tasks/{id}/add_comment/
        """
        task = self.get_object()

        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Comment.objects.create(
            task=task,
            author=request.user,
            content=serializer.validated_data['content'],
            parent_comment_id=serializer.validated_data.get('parent_comment')
        )

        # Invalidate cache
        cache_key = f'task_{task.id}'
        cache.delete(cache_key)

        return Response(
            {'message': 'Comment added successfully'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def upload_attachment(self, request, pk=None):
        """
        Upload an attachment to the task.
        Endpoint: /api/tasks/{id}/upload_attachment/
        """
        task = self.get_object()

        serializer = TaskAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        TaskAttachment.objects.create(
            task=task,
            uploaded_by=request.user,
            file=serializer.validated_data['file']
        )

        # Invalidate cache
        cache_key = f'task_{task.id}'
        cache.delete(cache_key)

        return Response(
            {'message': 'Attachment uploaded successfully'},
            status=status.HTTP_201_CREATED
        )


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for Comment model"""
    queryset = Comment.objects.select_related('task', 'author').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter comments by task if provided"""
        queryset = super().get_queryset()
        task_id = self.request.query_params.get('task', None)
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        return queryset

    def perform_create(self, serializer):
        """Create comment with current user as author"""
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Mark comment as edited when updated"""
        serializer.save(is_edited=True)
