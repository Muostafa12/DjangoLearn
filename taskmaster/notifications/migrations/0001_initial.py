"""
Initial migrations for notifications app.
Creates Notification model with GenericForeignKey.
"""

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('task_created', 'Task Created'), ('task_updated', 'Task Updated'), ('task_assigned', 'Task Assigned'), ('task_completed', 'Task Completed'), ('task_overdue', 'Task Overdue'), ('comment_added', 'Comment Added'), ('comment_reply', 'Comment Reply'), ('project_invitation', 'Project Invitation'), ('mention', 'Mention')], max_length=50, verbose_name='notification type')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('message', models.TextField(verbose_name='message')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('is_read', models.BooleanField(default=False, verbose_name='is read')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='read at')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL, verbose_name='recipient')),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to=settings.AUTH_USER_MODEL, verbose_name='sender')),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
                'db_table': 'notifications',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', '-created_at'], name='notificatio_recipie_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['recipient', 'is_read'], name='notificatio_recipie_is_read_idx'),
        ),
    ]
