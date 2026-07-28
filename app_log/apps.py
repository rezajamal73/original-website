from django.apps import AppConfig


class AppLogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_log"
    verbose_name = "📖 لاگ سیستم"

    def ready(self):
        import app_log.signals