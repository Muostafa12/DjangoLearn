"""
Initial migrations for tasks app.
Creates Task, Comment, and TaskAttachment models.
"""

from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('projects', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('status', models.CharField(choices=[('todo', 'To Do'), ('in_progress', 'In Progress'), ('review', 'In Review'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='todo', max_length=20, verbose_name='status')),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20, verbose_name='priority')),
                ('estimated_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='estimated hours')),
                ('actual_hours', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='actual hours')),
                ('completion_percentage', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='completion percentage')),
                ('due_date', models.DateTimeField(blank=True, null=True, verbose_name='due date')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='started at')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='completed at')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignees', models.ManyToManyField(blank=True, related_name='assigned_tasks', to=settings.AUTH_USER_MODEL, verbose_name='assignees')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_tasks', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('parent_task', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='tasks.task', verbose_name='parent task')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='projects.project', verbose_name='project')),
            ],
            options={
                'verbose_name': 'task',
                'verbose_name_plural': 'tasks',
                'db_table': 'tasks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TaskAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='task_attachments/%Y/%m/%d/', verbose_name='file')),
                ('filename', models.CharField(max_length=255, verbose_name='filename')),
                ('file_size', models.IntegerField(help_text='Size in bytes', verbose_name='file size')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='tasks.task', verbose_name='task')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_attachments', to=settings.AUTH_USER_MODEL, verbose_name='uploaded by')),
            ],
            options={
                'verbose_name': 'task attachment',
                'verbose_name_plural': 'task attachments',
                'db_table': 'task_attachments',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='content')),
                ('is_edited', models.BooleanField(default=False, verbose_name='is edited')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL, verbose_name='author')),
                ('parent_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='tasks.comment', verbose_name='parent comment')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tasks.task', verbose_name='task')),
            ],
            options={
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'db_table': 'comments',
                'ordering': ['created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status', 'priority'], name='tasks_task_status_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['project', '-created_at'], name='tasks_task_project_idx'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['due_date'], name='tasks_task_due_date_idx'),
        ),
        migrations.AddIndex(
            model_name='comment',
            index=models.Index(fields=['task', 'created_at'], name='comments_co_task_idx'),
        ),
    ]
