"""
Serializers for the projects app.
"""

from rest_framework import serializers
from .models import Project, ProjectMember
from taskmaster.accounts.serializers import UserSerializer


class ProjectMemberSerializer(serializers.ModelSerializer):
    """Serializer for ProjectMember model"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'user_id', 'role', 'joined_at', 'can_manage_project']
        read_only_fields = ['id', 'joined_at', 'can_manage_project']


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for Project list view"""
    owner = UserSerializer(read_only=True)
    task_count = serializers.IntegerField(read_only=True)
    completed_task_count = serializers.IntegerField(read_only=True)
    completion_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'owner',
            'start_date', 'end_date', 'task_count',
            'completed_task_count', 'completion_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for Project detail view"""
    owner = UserSerializer(read_only=True)
    memberships = ProjectMemberSerializer(many=True, read_only=True)
    task_count = serializers.IntegerField(read_only=True)
    completed_task_count = serializers.IntegerField(read_only=True)
    completion_percentage = serializers.FloatField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'status', 'owner',
            'memberships', 'start_date', 'end_date',
            'task_count', 'completed_task_count',
            'completion_percentage', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating projects"""

    class Meta:
        model = Project
        fields = ['name', 'description', 'status', 'start_date', 'end_date']

    def create(self, validated_data):
        """Create project and add creator as owner"""
        user = self.context['request'].user
        project = Project.objects.create(owner=user, **validated_data)

        # Add creator as owner member
        ProjectMember.objects.create(
            project=project,
            user=user,
            role='owner'
        )

        return project
