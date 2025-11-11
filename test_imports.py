#!/usr/bin/env python3
"""
Quick test to check if all imports work correctly
"""
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, '/home/user/DjangoLearn')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskmaster.settings')

print("Testing imports...")

try:
    # Test settings import
    print("✓ Importing settings...")
    from taskmaster import settings

    # Test Django setup
    print("✓ Setting up Django...")
    import django
    django.setup()

    # Test model imports
    print("✓ Importing accounts models...")
    from taskmaster.accounts.models import User, UserProfile

    print("✓ Importing projects models...")
    from taskmaster.projects.models import Project, ProjectMember

    print("✓ Importing tasks models...")
    from taskmaster.tasks.models import Task, Comment, TaskAttachment

    print("✓ Importing notifications models...")
    from taskmaster.notifications.models import Notification

    # Test serializer imports
    print("✓ Importing serializers...")
    from taskmaster.accounts.serializers import UserSerializer
    from taskmaster.projects.serializers import ProjectListSerializer
    from taskmaster.tasks.serializers import TaskListSerializer
    from taskmaster.notifications.serializers import NotificationSerializer

    # Test view imports
    print("✓ Importing views...")
    from taskmaster.accounts.views import UserViewSet
    from taskmaster.projects.views import ProjectViewSet
    from taskmaster.tasks.views import TaskViewSet
    from taskmaster.notifications.views import NotificationViewSet

    # Test Celery
    print("✓ Importing Celery...")
    from taskmaster.celery import app as celery_app

    print("\n✅ All imports successful!")
    print("Django version:", django.get_version())

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
