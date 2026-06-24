from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group
from app_core.models import UserProxy, GroupProxy


# ================================
#   حذف مدل‌های اصلی
# ================================
admin.site.unregister(User)
admin.site.unregister(Group)


# ================================
#   GLOBAL DELETE BUTTON
# ================================
def admin_delete_button(obj):
    url = reverse(f"admin:{obj._meta.app_label}_{obj._meta.model_name}_delete", args=[obj.pk])
    return format_html(
        '''
        <a href="{}"
           style="
                background:#d7263d;
                color:white;
                padding:6px 10px;
                border-radius:8px;
                text-decoration:none;
                font-weight:bold;
                display:inline-flex;
                align-items:center;
                gap:5px;
                box-shadow:0 2px 5px rgba(0,0,0,0.2);
           ">
            🗑
        </a>
        ''',
        url
    )
admin_delete_button.short_description = ""


# ================================
#   فرم ساخت کاربر جدید
# ================================
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = UserProxy
        fields = ("username", "email")
        labels = {
            "username": "نام کاربری",
            "email": "ایمیل",
        }


# ================================
#   فرم ویرایش کاربر
# ================================
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = UserProxy
        fields = "__all__"
        labels = {
            "username": "نام کاربری",
            "email": "ایمیل",
            "first_name": "نام",
            "last_name": "نام خانوادگی",
            "is_active": "فعال",
            "is_staff": "کارمند",
            "is_superuser": "مدیر کل",
            "groups": "گروه‌ها",
            "user_permissions": "مجوزها",
            "last_login": "آخرین ورود",
            "date_joined": "تاریخ عضویت",
        }


# ================================
#   USERPROXY ADMIN (Pro UI — blog style)
# ================================
@admin.register(UserProxy)
class UserProxyAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = UserProxy
    actions = None

    list_display = (
        "colored_username",
        "colored_email",
        "colored_name",
        "is_active_icon",
        "date_joined_icon",
        "delete_button",
    )

    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        ("🔐 اطلاعات ورود", {
            "fields": ("username", "password"),
        }),
        ("👤 اطلاعات شخصی", {
            "fields": ("first_name", "last_name", "email"),
        }),
        ("🛡️ سطح دسترسی‌ها", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("⏱️ زمان‌ها", {
            "fields": ("last_login", "date_joined"),
        }),
    )

    add_fieldsets = (
        ("➕ ساخت کاربر جدید", {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")

    # --------------------------------
    #   STYLED COLUMNS (blog style)
    # --------------------------------
    def colored_username(self, obj):
        return format_html("<b style='color:#1A73E8'>{}</b>", obj.username)
    colored_username.short_description = "نام کاربری"

    def colored_email(self, obj):
        return format_html("<span style='color:#0B8043'>{}</span>", obj.email)
    colored_email.short_description = "ایمیل"

    def colored_name(self, obj):
        full = f"{obj.first_name} {obj.last_name}".strip()
        return format_html("<span style='color:#5C2E91'>{}</span>", full if full else "—")
    colored_name.short_description = "نام و نام خانوادگی"

    def is_active_icon(self, obj):
        return "✅" if obj.is_active else "⛔"

    is_active_icon.short_description = "فعال"

    def is_staff_icon(self, obj):
        return "👤" if obj.is_staff else "—"

    is_staff_icon.short_description = "کارمند"

    def date_joined_icon(self, obj):
        return format_html("📅 {}", obj.date_joined.strftime("%Y-%m-%d"))
    date_joined_icon.short_description = "تاریخ عضویت"

    def delete_button(self, obj):
        return admin_delete_button(obj)


# ================================
#   GROUPPROXY ADMIN (Pro UI — blog style)
# ================================
@admin.register(GroupProxy)
class GroupProxyAdmin(admin.ModelAdmin):
    actions = None

    list_display = ("name_icon", "delete_button")
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("permissions",)

    fieldsets = (
        ("👥 اطلاعات گروه", {
            "fields": ("name",),
        }),
        ("🔑 دسترسی‌ها", {
            "fields": ("permissions",),
        }),
    )

    def name_icon(self, obj):
        return format_html("👥 <b>{}</b>", obj.name)
    name_icon.short_description = "نام گروه"

    def delete_button(self, obj):
        return admin_delete_button(obj)
