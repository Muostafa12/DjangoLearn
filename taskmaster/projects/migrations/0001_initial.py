"""
Initial migrations for projects app.
Creates Project and ProjectMember models.
"""

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('status', models.CharField(choices=[('planning', 'Planning'), ('active', 'Active'), ('on_hold', 'On Hold'), ('completed', 'Completed'), ('archived', 'Archived')], default='planning', max_length=20, verbose_name='status')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='start date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='end date')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_projects', to=settings.AUTH_USER_MODEL, verbose_name='owner')),
            ],
            options={
                'verbose_name': 'project',
                'verbose_name_plural': 'projects',
                'db_table': 'projects',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProjectMember',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member'), ('viewer', 'Viewer')], default='member', max_length=20, verbose_name='role')),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memberships', to='projects.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_memberships', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'project member',
                'verbose_name_plural': 'project members',
                'db_table': 'project_members',
                'ordering': ['project', '-joined_at'],
                'unique_together': {('project', 'user')},
            },
        ),
        migrations.AddField(
            model_name='project',
            name='members',
            field=models.ManyToManyField(related_name='projects', through='projects.ProjectMember', to=settings.AUTH_USER_MODEL, verbose_name='members'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['status', '-created_at'], name='projects_pr_status_idx'),
        ),
        migrations.AddIndex(
            model_name='project',
            index=models.Index(fields=['owner', '-created_at'], name='projects_pr_owner_idx'),
        ),
    ]
