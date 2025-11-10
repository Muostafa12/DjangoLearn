from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'taskmaster.accounts'

    def ready(self):
        import taskmaster.accounts.signals  # noqa
