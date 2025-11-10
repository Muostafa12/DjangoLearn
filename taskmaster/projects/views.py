"""
Views for the projects app.
Demonstrates viewsets with caching and custom actions.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.db.models import Q, Count, Prefetch
from .models import Project, ProjectMember
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    ProjectMemberSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project model.
    Demonstrates caching, filtering, and custom actions.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get projects where user is a member.
        Demonstrates query optimization.
        """
        user = self.request.user
        queryset = Project.objects.filter(
            Q(owner=user) | Q(members=user)
        ).distinct().select_related('owner').prefetch_related(
            'memberships__user',
            'tasks'
        )

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        return queryset

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action == 'create':
            return ProjectCreateSerializer
        return ProjectDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        """Retrieve with Redis caching"""
        project_id = kwargs.get('pk')
        cache_key = f'project_{project_id}'

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        cache.set(cache_key, data, 300)  # Cache for 5 minutes

        return Response(data)

    def perform_create(self, serializer):
        """Create project with current user as owner"""
        serializer.save()

    def perform_update(self, serializer):
        """Update and invalidate cache"""
        instance = serializer.save()
        cache_key = f'project_{instance.id}'
        cache.delete(cache_key)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """
        Add a member to the project.
        Endpoint: /api/projects/{id}/add_member/
        """
        project = self.get_object()

        # Check if user can manage project
        membership = ProjectMember.objects.filter(
            project=project,
            user=request.user
        ).first()

        if not membership or not membership.can_manage_project:
            return Response(
                {'error': 'You do not have permission to add members'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ProjectMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if user is already a member
        user_id = serializer.validated_data['user_id']
        if ProjectMember.objects.filter(project=project, user_id=user_id).exists():
            return Response(
                {'error': 'User is already a member'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ProjectMember.objects.create(
            project=project,
            user_id=user_id,
            role=serializer.validated_data.get('role', 'member')
        )

        # Invalidate cache
        cache_key = f'project_{project.id}'
        cache.delete(cache_key)

        return Response(
            {'message': 'Member added successfully'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """
        Remove a member from the project.
        Endpoint: /api/projects/{id}/remove_member/
        """
        project = self.get_object()

        # Check permissions
        membership = ProjectMember.objects.filter(
            project=project,
            user=request.user
        ).first()

        if not membership or not membership.can_manage_project:
            return Response(
                {'error': 'You do not have permission to remove members'},
                status=status.HTTP_403_FORBIDDEN
            )

        user_id = request.data.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Cannot remove owner
        if project.owner_id == user_id:
            return Response(
                {'error': 'Cannot remove project owner'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ProjectMember.objects.filter(
            project=project,
            user_id=user_id
        ).delete()

        # Invalidate cache
        cache_key = f'project_{project.id}'
        cache.delete(cache_key)

        return Response(
            {'message': 'Member removed successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """
        Get project statistics.
        Endpoint: /api/projects/{id}/statistics/
        """
        project = self.get_object()

        stats = {
            'total_tasks': project.task_count,
            'completed_tasks': project.completed_task_count,
            'completion_percentage': project.completion_percentage,
            'total_members': project.members.count(),
            'tasks_by_status': {},
            'tasks_by_priority': {},
        }

        # Tasks by status
        tasks_by_status = project.tasks.values('status').annotate(count=Count('id'))
        for item in tasks_by_status:
            stats['tasks_by_status'][item['status']] = item['count']

        # Tasks by priority
        tasks_by_priority = project.tasks.values('priority').annotate(count=Count('id'))
        for item in tasks_by_priority:
            stats['tasks_by_priority'][item['priority']] = item['count']

        return Response(stats)
