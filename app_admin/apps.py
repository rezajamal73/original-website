from django.apps import AppConfig


class AppAdminConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app_admin"
    verbose_name = "🔐 مدیریت امنیت و دسترسی‌ها"

    def ready(self):
        from django.apps import apps

        axes_config = apps.get_app_config("axes")
        axes_config.verbose_name = "🛡️ گزارش‌های امنیتی و ورود"