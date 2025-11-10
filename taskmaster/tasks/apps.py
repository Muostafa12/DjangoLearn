from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskmaster.tasks'

    def ready(self):
        import taskmaster.tasks.signals  # noqa
