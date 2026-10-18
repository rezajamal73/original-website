
import hashlib
import logging
import uuid
import zipfile
from html import escape
from pathlib import Path

import jdatetime

from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseNotAllowed,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, render
from django.template import engines
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .backup_service import BackupService
from .models import Backup, BACKUP_DIRECTORY
from .restore_service import RestoreService


logger = logging.getLogger(__name__)
MAX_UPLOAD_SIZE = 2 * 1024**3


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):

    change_list_template = "admin/app_backup.html"

    list_display = (
        "file_name",
        "file_size_display",
        "created_at_jalali",
        "download_backup",
        "restore_backup",
        "restore_media_button",
        "restore_full_button",
        "delete_backup_button",
    )

    search_fields = ("file_name",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    list_per_page = 50

    readonly_fields = (
        "file_name",
        "file_size",
        "checksum",
        "created_at",
    )

    # ==========================================
    # Permissions
    # ==========================================

    def _is_superuser(self, request):
        return bool(
            request.user.is_authenticated
            and request.user.is_active
            and request.user.is_superuser
        )

    def _require_superuser(self, request):
        if not self._is_superuser(request):
            raise PermissionDenied(
                "فقط مدیر اصلی مجاز به مدیریت بکاپ است."
            )

    def has_module_permission(self, request):
        return self._is_superuser(request)

    def has_view_permission(self, request, obj=None):
        return self._is_superuser(request)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return self._is_superuser(request)

    # ==========================================
    # Helpers
    # ==========================================

    def _list_url(self):
        return reverse(
            "admin:app_backup_backup_changelist"
        )

    def _redirect_list(self):
        return HttpResponseRedirect(self._list_url())

    def _get_backup(self, backup_id):
        return get_object_or_404(
            Backup,
            pk=backup_id,
        )

    def _backup_exists_or_redirect(self, request, backup):
        if backup.file_exists:
            return True

        self.message_user(
            request,
            "فایل بکاپ وجود ندارد.",
            messages.ERROR,
        )
        return False

    def _confirmation_page(
        self,
        request,
        title,
        message,
        action_url,
        button_text,
        is_progress=False,
        is_danger=False,
    ):
        template = engines["django"].from_string(
            """
{% extends "admin/base_site.html" %}
{% block content %}

<div style="
    max-width:680px;
    margin:35px auto;
    padding:28px;
    border:1px solid #ddd;
    border-radius:14px;
    background:#fff;
    box-shadow:0 4px 18px rgba(0,0,0,.05);
">

    <h1 style="font-size:23px;margin-bottom:18px">
        {{ title }}
    </h1>

    <p style="
        line-height:2;
        font-size:14px;
        color:#444;
        white-space:pre-line;
    ">{{ message }}</p>

    <form
        id="backup-action-form"
        method="post"
        action="{{ action_url }}"
    >
        {% csrf_token %}

        <button
            id="backup-submit-button"
            type="submit"
            style="
                background:{% if is_danger %}#c62828{% else %}#176b43{% endif %};
                color:white;
                border:0;
                padding:12px 24px;
                border-radius:8px;
                cursor:pointer;
                font-weight:bold;
            "
        >{{ button_text }}</button>

        <a
            id="backup-cancel-link"
            href="{{ cancel_url }}"
            style="margin-right:18px;text-decoration:none"
        >انصراف</a>
    </form>

    {% if is_progress %}

    <div
        id="backup-progress-panel"
        style="
            display:none;
            margin-top:28px;
            padding:20px;
            border:1px solid #d8e7dd;
            background:#f5faf7;
            border-radius:12px;
        "
    >
        <strong>در حال پردازش عملیات...</strong>

        <div style="
            margin-top:15px;
            height:15px;
            background:#dce7e0;
            border-radius:20px;
            overflow:hidden;
            position:relative;
        ">
            <div class="backup-progress-animation"></div>
        </div>

        <p id="backup-elapsed-time">
            زمان سپری‌شده: ۰ ثانیه
        </p>

        <small>
            این نوار نشان‌دهنده فعال بودن عملیات است،
            نه درصد واقعی تکمیل.
        </small>
    </div>

    <style>
    .backup-progress-animation {
        position:absolute;
        top:0;
        bottom:0;
        width:35%;
        background:linear-gradient(
            90deg,#43a047,#81c784,#1b5e20
        );
        border-radius:20px;
        animation:backup-running 1.8s
            ease-in-out infinite alternate;
    }

    @keyframes backup-running {
        from {left:0%}
        to {left:65%}
    }
    </style>

    <script>
    (function () {
        var form = document.getElementById(
            "backup-action-form"
        );
        var button = document.getElementById(
            "backup-submit-button"
        );
        var panel = document.getElementById(
            "backup-progress-panel"
        );
        var label = document.getElementById(
            "backup-elapsed-time"
        );
        var cancel = document.getElementById(
            "backup-cancel-link"
        );

        if (!form || !button || !panel) return;

        var submitted = false;

        form.addEventListener("submit", function (event) {
            if (submitted) {
                event.preventDefault();
                return;
            }

            submitted = true;
            panel.style.display = "block";
            button.disabled = true;
            button.textContent = "در حال پردازش...";

            if (cancel) {
                cancel.style.pointerEvents = "none";
                cancel.style.opacity = "0.5";
            }

            var start = Date.now();

            function updateElapsed() {
                var seconds = Math.floor(
                    (Date.now() - start) / 1000
                );
                var minutes = Math.floor(seconds / 60);
                var remaining = seconds % 60;

                label.textContent =
                    "زمان سپری‌شده: " +
                    minutes + " دقیقه و " +
                    remaining + " ثانیه";
            }

            updateElapsed();
            window.setInterval(updateElapsed, 1000);
        });
    })();
    </script>

    {% endif %}

</div>
{% endblock %}
            """
        )

        return HttpResponse(
            template.render(
                {
                    "title": title,
                    "message": message,
                    "action_url": action_url,
                    "button_text": button_text,
                    "cancel_url": self._list_url(),
                    "is_progress": is_progress,
                    "is_danger": is_danger,
                },
                request,
            )
        )

    def _instruction_page(
        self,
        title,
        backup,
        description,
        command=None,
        warning=None,
    ):
        command_html = ""

        if command:
            command_html = (
                '<h3>دستور اجرای آفلاین</h3>'
                '<pre dir="ltr" style="'
                'padding:20px;'
                'background:#222;'
                'color:#fff;'
                'border-radius:10px;'
                'white-space:pre-wrap;'
                'overflow-wrap:anywhere;">'
                + escape(command)
                + '</pre>'
            )

        warning_html = ""

        if warning:
            warning_html = (
                '<div style="'
                'padding:15px;'
                'background:#fff3e0;'
                'border:1px solid #ffcc80;'
                'border-radius:8px;'
                'color:#9a3412;'
                'margin:20px 0;">'
                + escape(warning)
                + '</div>'
            )

        html = (
            '<div dir="rtl" style="'
            'max-width:850px;'
            'margin:45px auto;'
            'padding:25px;'
            'font-family:tahoma;'
            'line-height:2;'
            'border:1px solid #ddd;'
            'border-radius:14px;">'
            '<h2>'
            + escape(title)
            + '</h2>'
            '<p><strong>فایل بکاپ:</strong> '
            + escape(backup.file_name)
            + '</p>'
            '<p>'
            + escape(description)
            + '</p>'
            + warning_html
            + command_html
            + '<p>'
            'قبل از بازیابی واقعی، سایت و همه '
            'پردازش‌های نویسنده باید متوقف شوند.'
            '</p>'
            '<p>'
            'پس از بازیابی، اطلاعات و فایل‌های '
            'سایت را بررسی کنید و سپس سایت را '
            'مجدداً راه‌اندازی کنید.'
            '</p>'
            '<a href="'
            + escape(self._list_url(), quote=True)
            + '">بازگشت به فهرست بکاپ‌ها</a>'
            '</div>'
        )

        return HttpResponse(html)

    # ==========================================
    # List columns
    # ==========================================

    @admin.display(description="تاریخ")
    def created_at_jalali(self, obj):
        if not obj or not obj.created_at:
            return "تاریخ نامشخص"

        try:
            local = timezone.localtime(obj.created_at)
            jalali = jdatetime.datetime.fromgregorian(
                datetime=local
            )
            return format_html(
                '<strong>{}</strong>'
                '<div style="font-size:11px;color:#777">{}</div>',
                jalali.strftime("%Y/%m/%d %H:%M:%S"),
                local.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception:
            logger.exception("Invalid backup date")
            return "تاریخ نامعتبر"

    @admin.display(description="حجم فایل")
    def file_size_display(self, obj):
        return obj.size if obj else "نامشخص"

    @admin.display(description="دانلود")
    def download_backup(self, obj):
        if not obj or not obj.file_exists:
            return "فایل موجود نیست"

        return format_html(
            '<a class="button" href="{}">⬇ دانلود</a>',
            reverse(
                "admin:app_backup_download",
                args=[obj.pk],
            ),
        )

    @admin.display(description="بررسی بکاپ")
    def restore_backup(self, obj):
        if not obj or not obj.file_exists:
            return "فایل موجود نیست"

        return format_html(
            '<a class="button" href="{}">'
            '🔍 بررسی سلامت</a>',
            reverse(
                "admin:app_backup_restore",
                args=[obj.pk],
            ),
        )

    @admin.display(description="بازیابی فقط Media")
    def restore_media_button(self, obj):
        if not obj or not obj.file_exists:
            return "فایل موجود نیست"

        return format_html(
            '<a href="{}" style="'
            'display:inline-block;'
            'background:#00897b;'
            'color:white;'
            'padding:6px 12px;'
            'border-radius:7px;'
            'text-decoration:none;'
            'font-weight:bold;">'
            '🖼 بازیابی Media'
            '</a>',
            reverse(
                "admin:app_backup_restore_media",
                args=[obj.pk],
            ),
        )

    @admin.display(description="بازیابی Media + Database")
    def restore_full_button(self, obj):
        if not obj or not obj.file_exists:
            return "فایل موجود نیست"

        return format_html(
            '<a href="{}" style="'
            'display:inline-block;'
            'background:#1565c0;'
            'color:white;'
            'padding:6px 12px;'
            'border-radius:7px;'
            'text-decoration:none;'
            'font-weight:bold;">'
            '♻️ Media + Database'
            '</a>',
            reverse(
                "admin:app_backup_restore_full",
                args=[obj.pk],
            ),
        )

    @admin.display(description="حذف بکاپ")
    def delete_backup_button(self, obj):
        if not obj or not obj.pk:
            return "—"

        return format_html(
            '<a href="{}" style="'
            'display:inline-block;'
            'background:#c62828;'
            'color:white;'
            'padding:6px 12px;'
            'border-radius:7px;'
            'text-decoration:none;'
            'font-weight:bold;">'
            '🗑 حذف'
            '</a>',
            reverse(
                "admin:app_backup_delete_backup",
                args=[obj.pk],
            ),
        )

    # ==========================================
    # Custom URLs
    # ==========================================

    def get_urls(self):
        custom_urls = [
            path(
                "create/",
                self.admin_site.admin_view(
                    self.create_backup
                ),
                name="app_backup_create_backup",
            ),
            path(
                "upload/",
                self.admin_site.admin_view(
                    self.upload_backup_view
                ),
                name="app_backup_upload",
            ),
            path(
                "<int:backup_id>/download/",
                self.admin_site.admin_view(
                    self.download_backup_view
                ),
                name="app_backup_download",
            ),
            path(
                "<int:backup_id>/restore/",
                self.admin_site.admin_view(
                    self.restore_backup_view
                ),
                name="app_backup_restore",
            ),
            path(
                "<int:backup_id>/restore-media/",
                self.admin_site.admin_view(
                    self.restore_media_view
                ),
                name="app_backup_restore_media",
            ),
            path(
                "<int:backup_id>/restore-full/",
                self.admin_site.admin_view(
                    self.restore_full_view
                ),
                name="app_backup_restore_full",
            ),
            path(
                "<int:backup_id>/delete/",
                self.admin_site.admin_view(
                    self.delete_backup_view
                ),
                name="app_backup_delete_backup",
            ),
        ]
        return custom_urls + super().get_urls()

    # ==========================================
    # Create backup
    # ==========================================

    def create_backup(self, request):
        self._require_superuser(request)

        if request.method == "GET":
            return self._confirmation_page(
                request,
                "ایجاد نسخه پشتیبان",
                "یک نسخه پشتیبان از دیتابیس و "
                "فایل‌های رسانه‌ای سایت ساخته می‌شود.",
                reverse(
                    "admin:app_backup_create_backup"
                ),
                "🚀 شروع بکاپ‌گیری",
                is_progress=True,
            )

        if request.method != "POST":
            return HttpResponseNotAllowed(["GET", "POST"])

        try:
            BackupService().create_backup()
            self.message_user(
                request,
                "✅ نسخه پشتیبان با موفقیت ایجاد شد.",
                messages.SUCCESS,
            )
        except Exception:
            logger.exception("Backup creation failed")
            self.message_user(
                request,
                "❌ ایجاد بکاپ ناموفق بود. "
                "جزئیات در لاگ سرور ثبت شد.",
                messages.ERROR,
            )

        return self._redirect_list()

    # ==========================================
    # Upload backup
    # ==========================================

    def upload_backup_view(self, request):
        self._require_superuser(request)

        if request.method == "GET":
            return render(
                request,
                "admin/app_backup_upload.html",
            )

        if request.method != "POST":
            return HttpResponseNotAllowed(["GET", "POST"])

        uploaded = request.FILES.get("backup")

        if uploaded is None:
            self.message_user(
                request,
                "فایلی انتخاب نشده است.",
                messages.ERROR,
            )
            return self._redirect_list()

        if not uploaded.name.lower().endswith(".zip"):
            self.message_user(
                request,
                "فقط فایل ZIP مجاز است.",
                messages.ERROR,
            )
            return self._redirect_list()

        if uploaded.size > MAX_UPLOAD_SIZE:
            self.message_user(
                request,
                "حجم فایل بیش از حد مجاز است.",
                messages.ERROR,
            )
            return self._redirect_list()

        BACKUP_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = f"uploaded_{uuid.uuid4().hex}.zip"
        file_path = BACKUP_DIRECTORY / filename

        try:
            sha256 = hashlib.sha256()
            total_size = 0

            with file_path.open("xb") as output:
                for chunk in uploaded.chunks():
                    total_size += len(chunk)

                    if total_size > MAX_UPLOAD_SIZE:
                        raise ValueError(
                            "حجم فایل بیش از حد مجاز است."
                        )

                    sha256.update(chunk)
                    output.write(chunk)

            with zipfile.ZipFile(file_path, "r") as archive:
                if archive.testzip() is not None:
                    raise ValueError("فایل ZIP خراب است.")

                database_files = [
                    name
                    for name in archive.namelist()
                    if (
                        name.startswith("Database/")
                        and name.endswith(".sqlite3")
                        and len(Path(name).parts) == 2
                    )
                ]

                if len(database_files) != 1:
                    raise ValueError(
                        "ساختار دیتابیس بکاپ معتبر نیست."
                    )

            Backup.objects.create(
                file_name=filename,
                file_size=total_size,
                checksum=sha256.hexdigest(),
            )

            self.message_user(
                request,
                "✅ فایل بکاپ بارگذاری و ثبت شد.",
                messages.SUCCESS,
            )

        except (
            OSError,
            ValueError,
            zipfile.BadZipFile,
            IntegrityError,
        ):
            logger.exception("Backup upload failed")
            file_path.unlink(missing_ok=True)

            self.message_user(
                request,
                "❌ بارگذاری بکاپ ناموفق بود.",
                messages.ERROR,
            )

        return self._redirect_list()

    # ==========================================
    # Download backup
    # ==========================================

    def download_backup_view(self, request, backup_id):
        self._require_superuser(request)

        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])

        backup = self._get_backup(backup_id)

        if not self._backup_exists_or_redirect(
            request, backup
        ):
            return self._redirect_list()

        return FileResponse(
            backup.backup_path.open("rb"),
            as_attachment=True,
            filename=backup.file_name,
            content_type="application/zip",
        )

    # ==========================================
    # Validate backup
    # ==========================================

    def restore_backup_view(self, request, backup_id):
        self._require_superuser(request)

        backup = self._get_backup(backup_id)

        if request.method == "GET":
            return self._confirmation_page(
                request,
                "بررسی سلامت نسخه پشتیبان",
                "این عملیات فقط فایل بکاپ و "
                "دیتابیس آن را بررسی می‌کند.\n\n"
                "هیچ اطلاعاتی روی سایت اصلی "
                "جایگزین نمی‌شود.",
                reverse(
                    "admin:app_backup_restore",
                    args=[backup.pk],
                ),
                "🔍 شروع بررسی سلامت",
                is_progress=True,
            )

        if request.method != "POST":
            return HttpResponseNotAllowed(["GET", "POST"])

        try:
            result = RestoreService(backup).restore()

            if (
                isinstance(result, dict)
                and result.get("valid") is True
                and result.get("restored") is False
            ):
                self.message_user(
                    request,
                    "✅ سلامت نسخه پشتیبان تأیید شد. "
                    "هیچ اطلاعاتی جایگزین نشده است.",
                    messages.SUCCESS,
                )
            else:
                self.message_user(
                    request,
                    "نتیجه اعتبارسنجی قابل تأیید نیست.",
                    messages.WARNING,
                )

        except Exception:
            logger.exception("Backup validation failed")
            self.message_user(
                request,
                "❌ بررسی سلامت بکاپ ناموفق بود.",
                messages.ERROR,
            )

        return self._redirect_list()

    # ==========================================
    # Restore Media only
    # ==========================================

    def restore_media_view(self, request, backup_id):
        self._require_superuser(request)

        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])

        backup = self._get_backup(backup_id)

        if not self._backup_exists_or_redirect(
            request, backup
        ):
            return self._redirect_list()

        command = (
            "cd /home/nkavoshc/project\n"
            "source /home/nkavoshc/virtualenv/"
            "project/3.12/bin/activate\n"
            "python -m "
            "app_backup.management.restore_backup_offline "
            f"{backup.pk} "
            "--media-only --confirm --offline-verified"
        )

        return self._instruction_page(
            title="🖼 بازیابی فقط Media",
            backup=backup,
            description=(
                "در این حالت فقط تصاویر، ویدئوها و "
                "سایر فایل‌های پوشه Media از بکاپ "
                "بازیابی می‌شوند. "
                "دیتابیس فعلی تغییر نمی‌کند."
            ),
            command=command,
            warning=(
                "هشدار: فایل‌های Media فعلی با "
                "فایل‌های بکاپ جایگزین می‌شوند. "
                "قبل از اجرای دستور، سایت، کرون‌ها "
                "و همه پردازش‌های نویسنده را متوقف کنید. "
                "نسخه قبلی Media در پوشه نجات "
                "نگهداری خواهد شد."
            ),
        )

    # ==========================================
    # Restore Media + Database
    # ==========================================

    def restore_full_view(self, request, backup_id):
        self._require_superuser(request)

        if request.method != "GET":
            return HttpResponseNotAllowed(["GET"])

        backup = self._get_backup(backup_id)

        if not self._backup_exists_or_redirect(
            request, backup
        ):
            return self._redirect_list()

        command = (
            "cd /home/nkavoshc/project\n"
            "source /home/nkavoshc/virtualenv/"
            "project/3.12/bin/activate\n"
            "python -m "
            "app_backup.management.restore_backup_offline "
            f"{backup.pk} "
            "--confirm --offline-verified"
        )

        return self._instruction_page(
            title="♻️ بازیابی Media + Database",
            backup=backup,
            description=(
                "این حالت دیتابیس و تمام فایل‌های "
                "Media فعلی سایت را با محتوای "
                "نسخه پشتیبان جایگزین می‌کند."
            ),
            command=command,
            warning=(
                "هشدار: این عملیات واقعی است. "
                "قبل از اجرای دستور، سایت، کرون‌ها "
                "و تمام پردازش‌های نویسنده دیتابیس "
                "باید متوقف شوند. "
                "گزینه --offline-verified صرفاً "
                "تأیید دستی توقف آن‌هاست."
            ),
        )

    # ==========================================
    # Delete backup
    # ==========================================

    def delete_backup_view(self, request, backup_id):
        self._require_superuser(request)

        backup = self._get_backup(backup_id)

        if request.method == "GET":
            return self._confirmation_page(
                request,
                "🗑 حذف نسخه پشتیبان",
                "آیا از حذف این نسخه پشتیبان "
                "اطمینان دارید؟\n\n"
                f"نام فایل: {backup.file_name}\n\n"
                "فایل ZIP و رکورد آن حذف می‌شوند.\n"
                "این عملیات قابل بازگشت نیست.",
                reverse(
                    "admin:app_backup_delete_backup",
                    args=[backup.pk],
                ),
                "🗑 تأیید حذف بکاپ",
                is_danger=True,
            )

        if request.method != "POST":
            return HttpResponseNotAllowed(["GET", "POST"])

        try:
            backup_root = Path(
                BACKUP_DIRECTORY
            ).resolve(strict=True)

            filename = str(backup.file_name)

            if (
                not filename
                or filename in (".", "..")
                or Path(filename).name != filename
                or "/" in filename
                or "\\" in filename
                or not filename.lower().endswith(".zip")
            ):
                raise ValueError(
                    "Invalid backup filename."
                )

            file_path = Path(backup.backup_path)

            if file_path.is_symlink():
                raise ValueError(
                    "Backup symlink deletion is forbidden."
                )

            resolved = file_path.resolve(strict=False)

            if (
                resolved.parent != backup_root
                or resolved.name != filename
            ):
                raise ValueError(
                    "Backup path is invalid."
                )

            if resolved.exists():
                if not resolved.is_file():
                    raise ValueError(
                        "Backup path is not a regular file."
                    )
                resolved.unlink()

            backup.delete()

            logger.info(
                "Backup deleted by user_id=%s, "
                "backup_id=%s, filename=%s",
                request.user.pk,
                backup_id,
                filename,
            )

            self.message_user(
                request,
                "✅ نسخه پشتیبان و رکورد آن حذف شدند.",
                messages.SUCCESS,
            )

        except Exception:
            logger.exception(
                "Backup deletion failed: %s",
                backup_id,
            )

            self.message_user(
                request,
                "❌ حذف بکاپ ناموفق بود. "
                "جزئیات در لاگ سرور ثبت شد.",
                messages.ERROR,
            )

        return self._redirect_list()
