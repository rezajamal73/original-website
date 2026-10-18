
"""
Backup Administration
Parsa Novin Kavosh
Django 6 compatible

Features:
- Create backups
- Upload and validate backup archives
- Download backups
- Validate backup health without restoring live data
- Delete backup ZIP and database record
- Show animated progress while backup is being created

Security:
- Superuser-only operations
- CSRF-protected POST operations
- Confirmation before deletion
- Backup path validation
"""

import hashlib
import logging
import uuid
import zipfile

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

    # ======================================================
    # PERMISSIONS
    # ======================================================

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

    # ======================================================
    # HELPERS
    # ======================================================

    def _list_url(self):
        return reverse(
            "admin:app_backup_backup_changelist"
        )

    def _redirect_list(self):
        return HttpResponseRedirect(
            self._list_url()
        )

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
        """
        Render a CSRF-protected confirmation page.

        When is_progress=True, show an animated,
        indeterminate progress bar after submission.

        The bar does not invent a completion percentage.
        """

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

    <h1 style="
        font-size:23px;
        margin-bottom:18px;
    ">
        {{ title }}
    </h1>

    <p style="
        line-height:2;
        font-size:14px;
        color:#444;
        white-space:pre-line;
    ">
        {{ message }}
    </p>

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
        >
            {{ button_text }}
        </button>

        <a
            id="backup-cancel-link"
            href="{{ cancel_url }}"
            style="
                margin-right:18px;
                text-decoration:none;
            "
        >
            انصراف
        </a>

    </form>

    {% if is_progress %}

    <div
        id="backup-progress-panel"
        role="status"
        aria-live="polite"
        style="
            display:none;
            margin-top:28px;
            padding:20px;
            border:1px solid #d8e7dd;
            background:#f5faf7;
            border-radius:12px;
        "
    >

        <div style="
            font-weight:bold;
            margin-bottom:12px;
            color:#176b43;
        ">
            در حال ساخت نسخه پشتیبان...
        </div>

        <div
            role="progressbar"
            aria-label="عملیات ساخت بکاپ در حال انجام است"
            style="
                width:100%;
                height:15px;
                background:#dce7e0;
                border-radius:20px;
                overflow:hidden;
                position:relative;
            "
        >
            <div class="backup-progress-animation"></div>
        </div>

        <div
            id="backup-elapsed-time"
            style="
                margin-top:12px;
                font-size:13px;
                color:#555;
            "
        >
            زمان سپری‌شده: ۰ ثانیه
        </div>

        <p style="
            margin-top:12px;
            font-size:12px;
            color:#666;
            line-height:1.9;
        ">
            سرور در حال آماده‌سازی فایل ZIP است.
            مدت انجام عملیات به حجم دیتابیس
            و فایل‌های رسانه‌ای بستگی دارد.
            لطفاً صفحه را نبندید و دوباره
            روی دکمه کلیک نکنید.
        </p>

        <p style="
            font-size:12px;
            color:#777;
        ">
            این نوار نشان‌دهنده فعال بودن عملیات است،
            نه درصد واقعی تکمیل بکاپ.
        </p>

    </div>

    <style>
        .backup-progress-animation {
            position:absolute;
            top:0;
            bottom:0;
            width:35%;
            background:linear-gradient(
                90deg,
                #43a047,
                #81c784,
                #1b5e20
            );
            border-radius:20px;
            animation:backup-running 1.8s
                ease-in-out infinite alternate;
        }

        @keyframes backup-running {
            from {
                left:0%;
            }

            to {
                left:65%;
            }
        }
    </style>

    <script>
    (function () {
        "use strict";

        var form = document.getElementById(
            "backup-action-form"
        );

        var button = document.getElementById(
            "backup-submit-button"
        );

        var panel = document.getElementById(
            "backup-progress-panel"
        );

        var timerLabel = document.getElementById(
            "backup-elapsed-time"
        );

        var cancel = document.getElementById(
            "backup-cancel-link"
        );

        if (!form || !button || !panel) {
            return;
        }

        var submitted = false;

        form.addEventListener("submit", function (event) {
            if (submitted) {
                event.preventDefault();
                return;
            }

            submitted = true;

            panel.style.display = "block";

            button.style.opacity = "0.65";
            button.style.cursor = "not-allowed";
            button.textContent = "در حال پردازش...";

            if (cancel) {
                cancel.style.pointerEvents = "none";
                cancel.style.opacity = "0.5";
            }

            var startTime = Date.now();

            function updateElapsed() {
                var seconds = Math.floor(
                    (Date.now() - startTime) / 1000
                );

                var minutes = Math.floor(
                    seconds / 60
                );

                var remaining = seconds % 60;

                timerLabel.textContent =
                    "زمان سپری‌شده: " +
                    minutes +
                    " دقیقه و " +
                    remaining +
                    " ثانیه";
            }

            updateElapsed();

            window.setInterval(
                updateElapsed,
                1000
            );
        });
    })();
    </script>

    {% endif %}

</div>

{% endblock %}
            """
        )

        html = template.render(
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

        return HttpResponse(html)

    # ======================================================
    # DATE DISPLAY
    # ======================================================

    @admin.display(description="تاریخ")
    def created_at_jalali(self, obj):

        if not obj or not obj.created_at:
            return "تاریخ نامشخص"

        try:
            local_time = timezone.localtime(
                obj.created_at
            )

            jalali = jdatetime.datetime.fromgregorian(
                datetime=local_time
            )

            return format_html(
                '<div style="line-height:1.5">'
                '<strong>{}</strong>'
                '<div style="font-size:11px;color:#777">'
                '{}</div></div>',
                jalali.strftime("%Y/%m/%d %H:%M:%S"),
                local_time.strftime("%Y-%m-%d %H:%M:%S"),
            )

        except Exception:
            logger.exception(
                "Invalid backup date."
            )
            return "تاریخ نامعتبر"

    # ======================================================
    # FILE SIZE
    # ======================================================

    @admin.display(description="حجم فایل")
    def file_size_display(self, obj):

        if not obj:
            return "نامشخص"

        return obj.size

    # ======================================================
    # DOWNLOAD BUTTON
    # ======================================================

    @admin.display(description="دانلود")
    def download_backup(self, obj):

        if not obj or not obj.file_exists:
            return "فایل موجود نیست"

        return format_html(
            '<a class="button" href="{}">'
            '⬇ دانلود</a>',
            reverse(
                "admin:app_backup_download",
                args=[obj.pk],
            ),
        )

    # ======================================================
    # VALIDATE BUTTON
    # ======================================================

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

    # ======================================================
    # DELETE BUTTON
    # ======================================================

    @admin.display(description="حذف بکاپ")
    def delete_backup_button(self, obj):

        if not obj or not obj.pk:
            return "—"

        url = reverse(
            "admin:app_backup_delete_backup",
            args=[obj.pk],
        )

        return format_html(
            '<a href="{}" '
            'style="'
            'display:inline-block;'
            'background:#c62828;'
            'color:#fff;'
            'padding:6px 12px;'
            'border-radius:7px;'
            'text-decoration:none;'
            'font-weight:bold;'
            'white-space:nowrap;'
            '">'
            '🗑 حذف</a>',
            url,
        )

    # ======================================================
    # CUSTOM URLS
    # ======================================================

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
                "<int:backup_id>/delete/",
                self.admin_site.admin_view(
                    self.delete_backup_view
                ),
                name="app_backup_delete_backup",
            ),
        ]

        return custom_urls + super().get_urls()

    # ======================================================
    # CREATE BACKUP
    # ======================================================

    def create_backup(self, request):

        self._require_superuser(request)

        if request.method == "GET":
            return self._confirmation_page(
                request,
                "ایجاد نسخه پشتیبان",
                (
                    "یک نسخه پشتیبان جدید از دیتابیس "
                    "و فایل‌های رسانه‌ای ساخته می‌شود.\n\n"
                    "بعد از تأیید، نوار وضعیت عملیات "
                    "و زمان سپری‌شده نمایش داده می‌شود."
                ),
                reverse(
                    "admin:app_backup_create_backup"
                ),
                "🚀 شروع بکاپ‌گیری",
                is_progress=True,
            )

        if request.method != "POST":
            return HttpResponseNotAllowed(
                ["GET", "POST"]
            )

        try:
            BackupService().create_backup()

            self.message_user(
                request,
                "✅ نسخه پشتیبان با موفقیت ایجاد شد.",
                messages.SUCCESS,
            )

        except Exception:
            logger.exception(
                "Backup creation failed."
            )

            self.message_user(
                request,
                "❌ ایجاد بکاپ ناموفق بود. "
                "جزئیات در لاگ سرور ثبت شد.",
                messages.ERROR,
            )

        return self._redirect_list()

    # ======================================================
    # UPLOAD BACKUP
    # ======================================================

    def upload_backup_view(self, request):

        self._require_superuser(request)

        if request.method == "GET":
            return render(
                request,
                "admin/app_backup_upload.html",
            )

        if request.method != "POST":
            return HttpResponseNotAllowed(
                ["GET", "POST"]
            )

        uploaded_file = request.FILES.get(
            "backup"
        )

        if uploaded_file is None:
            self.message_user(
                request,
                "فایلی انتخاب نشده است.",
                messages.ERROR,
            )
            return self._redirect_list()

        if not uploaded_file.name.lower().endswith(
            ".zip"
        ):
            self.message_user(
                request,
                "فقط فایل ZIP مجاز است.",
                messages.ERROR,
            )
            return self._redirect_list()

        if uploaded_file.size > MAX_UPLOAD_SIZE:
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

        filename = (
            f"uploaded_{uuid.uuid4().hex}.zip"
        )

        file_path = BACKUP_DIRECTORY / filename

        try:
            sha256 = hashlib.sha256()
            total_size = 0

            with file_path.open("xb") as output:

                for chunk in uploaded_file.chunks():

                    total_size += len(chunk)

                    if total_size > MAX_UPLOAD_SIZE:
                        raise ValueError(
                            "حجم فایل بیش از حد مجاز است."
                        )

                    sha256.update(chunk)
                    output.write(chunk)

            with zipfile.ZipFile(
                file_path,
                "r",
            ) as archive:

                if archive.testzip() is not None:
                    raise ValueError(
                        "فایل ZIP خراب است."
                    )

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
                "✅ فایل بکاپ بارگذاری و ثبت شد. "
                "برای بررسی سلامت دیتابیس از "
                "گزینه بررسی بکاپ استفاده کنید.",
                messages.SUCCESS,
            )

        except (
            OSError,
            ValueError,
            zipfile.BadZipFile,
            IntegrityError,
        ):
            logger.exception(
                "Backup upload failed."
            )

            file_path.unlink(
                missing_ok=True
            )

            self.message_user(
                request,
                "❌ بارگذاری بکاپ ناموفق بود. "
                "فایل یا ساختار آن را بررسی کنید.",
                messages.ERROR,
            )

        return self._redirect_list()

    # ======================================================
    # DOWNLOAD BACKUP
    # ======================================================

    def download_backup_view(
        self,
        request,
        backup_id,
    ):

        self._require_superuser(request)

        if request.method != "GET":
            return HttpResponseNotAllowed(
                ["GET"]
            )

        backup = get_object_or_404(
            Backup,
            pk=backup_id,
        )

        if not backup.file_exists:
            self.message_user(
                request,
                "فایل بکاپ وجود ندارد.",
                messages.ERROR,
            )
            return self._redirect_list()

        return FileResponse(
            backup.backup_path.open("rb"),
            as_attachment=True,
            filename=backup.file_name,
            content_type="application/zip",
        )

    # ======================================================
    # VALIDATE BACKUP - NO LIVE RESTORE
    # ======================================================

    def restore_backup_view(
        self,
        request,
        backup_id,
    ):

        self._require_superuser(request)

        backup = get_object_or_404(
            Backup,
            pk=backup_id,
        )

        if request.method == "GET":
            return self._confirmation_page(
                request,
                "بررسی سلامت نسخه پشتیبان",
                (
                    "این عملیات فقط فایل بکاپ و "
                    "سلامت دیتابیس آن را بررسی می‌کند.\n\n"
                    "هیچ اطلاعاتی روی سایت اصلی "
                    "بازیابی یا جایگزین نمی‌شود."
                ),
                reverse(
                    "admin:app_backup_restore",
                    args=[backup.pk],
                ),
                "🔍 شروع بررسی سلامت",
                is_progress=True,
            )

        if request.method != "POST":
            return HttpResponseNotAllowed(
                ["GET", "POST"]
            )

        try:
            result = RestoreService(
                backup
            ).restore()

            if (
                isinstance(result, dict)
                and result.get("valid") is True
                and result.get("restored") is False
            ):

                self.message_user(
                    request,
                    "✅ سلامت نسخه پشتیبان تأیید شد. "
                    "هیچ اطلاعاتی روی سایت "
                    "اصلی جایگزین نشده است.",
                    messages.SUCCESS,
                )

            else:
                self.message_user(
                    request,
                    "نتیجه اعتبارسنجی قابل تأیید نیست. "
                    "هیچ بازیابی انجام نشد.",
                    messages.WARNING,
                )

        except Exception:
            logger.exception(
                "Backup validation failed."
            )

            self.message_user(
                request,
                "❌ بررسی سلامت بکاپ ناموفق بود. "
                "جزئیات در لاگ سرور ثبت شد.",
                messages.ERROR,
            )

        return self._redirect_list()

    # ======================================================
    # DELETE BACKUP
    # ======================================================

    def delete_backup_view(
        self,
        request,
        backup_id,
    ):
        """
        Delete the backup archive and its database record.

        GET:
            Display confirmation.

        POST:
            Validate path.
            Delete ZIP.
            Delete database record.

        Only superusers are allowed.
        """

        self._require_superuser(request)

        backup = get_object_or_404(
            Backup,
            pk=backup_id,
        )

        if request.method == "GET":

            filename = str(
                backup.file_name
            )

            return self._confirmation_page(
                request,
                "🗑 حذف نسخه پشتیبان",
                (
                    "آیا از حذف این نسخه پشتیبان "
                    "اطمینان دارید؟\n\n"
                    f"نام فایل: {filename}\n\n"
                    "با تأیید این عملیات، فایل ZIP "
                    "از فضای هاست حذف می‌شود و "
                    "رکورد مربوط به آن نیز "
                    "از فهرست بکاپ‌ها پاک خواهد شد.\n\n"
                    "این عملیات قابل بازگشت نیست."
                ),
                reverse(
                    "admin:app_backup_delete_backup",
                    args=[backup.pk],
                ),
                "🗑 تأیید حذف بکاپ",
                is_danger=True,
            )

        if request.method != "POST":
            return HttpResponseNotAllowed(
                ["GET", "POST"]
            )

        try:
            backup_root = Path(
                BACKUP_DIRECTORY
            ).resolve(strict=True)

            filename = str(
                backup.file_name
            )

            # Reject absolute paths and path traversal.
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

            file_path = Path(
                backup.backup_path
            )

            # Never delete a symlink.
            if file_path.is_symlink():
                raise ValueError(
                    "Backup symlink deletion is forbidden."
                )

            resolved_path = file_path.resolve(
                strict=False
            )

            # Only files directly inside BACKUP_DIRECTORY
            # can be deleted.
            if resolved_path.parent != backup_root:
                raise ValueError(
                    "Backup path is outside backup directory."
                )

            if resolved_path.name != filename:
                raise ValueError(
                    "Backup filename does not match path."
                )

            if resolved_path.exists():

                if not resolved_path.is_file():
                    raise ValueError(
                        "Backup path is not a regular file."
                    )

                resolved_path.unlink()

            # Delete database record only after
            # successful file removal.
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
                "✅ نسخه پشتیبان و رکورد آن "
                "با موفقیت حذف شدند.",
                messages.SUCCESS,
            )

        except Exception:
            logger.exception(
                "Backup deletion failed. "
                "backup_id=%s",
                backup_id,
            )

            self.message_user(
                request,
                "❌ حذف بکاپ ناموفق بود. "
                "فایل یا مسیر ذخیره‌سازی را بررسی کنید. "
                "جزئیات خطا در لاگ سرور ثبت شد.",
                messages.ERROR,
            )

        return self._redirect_list()
