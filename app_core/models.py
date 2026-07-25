from django.contrib.auth.models import User, Group




class UserProxy(User):
    """
    مدل پروکسی برای مدیریت بهتر کاربران در بخش مدیریت جنگو.
    شامل فارسی‌سازی، ترتیب نمایش، و ظاهر منظم‌تر.
    """
    class Meta:
        proxy = True
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ["username"]  # مرتب‌سازی پیش‌فرض بر اساس نام کاربری
        # برای زیبایی و حرفه‌ای‌تر شدن
        app_label = "app_core"


class GroupProxy(Group):
    """
    مدل پروکسی برای گروه‌های کاربری جهت فارسی‌سازی و بهبود مدیریت در پنل ادمین.
    """
    class Meta:
        proxy = True
        verbose_name = "گروه کاربری"
        verbose_name_plural = "گروه‌های کاربری"
        ordering = ["name"]  # مرتب‌سازی پیش‌فرض بر اساس نام گروه
        app_label = "app_core"



