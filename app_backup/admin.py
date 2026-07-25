import hashlib
import shutil
from pathlib import Path

import jdatetime

from django.conf import settings
from django.contrib import admin, messages
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html

from .backup_service import BackupService
from .models import Backup, BACKUP_DIRECTORY
from .restore_service import RestoreService


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):

    change_list_template = "admin/app_backup.html"

    list_display = (
        "file_name",
        "file_size_display",
        "created_at_jalali",
        "download_backup",
        "restore_backup",
    )

    search_fields = (
        "file_name",
    )

    list_filter = (
        "created_at",
    )

    readonly_fields = (
        "file_name",
        "file_size",
        "checksum",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    ####################################################
    # Permissions
    ####################################################

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    ####################################################
    # Date
    ####################################################

    def created_at_jalali(self, obj):

        local_time = timezone.localtime(
            obj.created_at,
        )

        jalali = jdatetime.datetime.fromgregorian(
            datetime=local_time,
        )

        return format_html(
            """
            <div style="line-height:1.5">
                <strong>{}</strong><br>
                <span style="font-size:11px;color:#777;">
                    {}
                </span>
            </div>
            """,
            jalali.strftime("%Y/%m/%d %H:%M:%S"),
            local_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

    created_at_jalali.short_description = "تاریخ"

    ####################################################
    # Size
    ####################################################

    @admin.display(description="حجم فایل")
    def file_size_display(self, obj):
        return obj.size

    ####################################################
    # Download
    ####################################################

    @admin.display(description="دانلود")
    def download_backup(self, obj):

        if not obj.file_exists:

            return format_html(
                '<span style="color:red;">❌ فایل وجود ندارد</span>'
            )

        return format_html(
            '<a class="button" href="{}">⬇ دانلود</a>',
            reverse(
                "admin:app_backup_download",
                args=[obj.pk],
            ),
        )

    ####################################################
    # Restore
    ####################################################

    @admin.display(description="بازیابی")
    def restore_backup(self, obj):

        if not obj.file_exists:

            return format_html(
                '<span style="color:red;">❌ فایل وجود ندارد</span>'
            )

        return format_html(
            '<a class="backup-restore-btn" href="{}">'
            '🔄 بازیابی'
            '</a>',
            reverse(
                "admin:app_backup_restore",
                args=[obj.pk],
            ),
        )

    ####################################################
    # URLs
    ####################################################

    def get_urls(self):

        urls = super().get_urls()

        custom_urls = [

            path(
                "create/",
                self.admin_site.admin_view(
                    self.create_backup,
                ),
                name="app_backup_create_backup",
            ),

            path(
                "upload/",
                self.admin_site.admin_view(
                    self.upload_backup_view,
                ),
                name="app_backup_upload",
            ),

            path(
                "<int:backup_id>/download/",
                self.admin_site.admin_view(
                    self.download_backup_view,
                ),
                name="app_backup_download",
            ),

            path(
                "<int:backup_id>/restore/",
                self.admin_site.admin_view(
                    self.restore_backup_view,
                ),
                name="app_backup_restore",
            ),
        ]

        return custom_urls + urls

    ####################################################
    # Create Backup
    ####################################################

    def create_backup(self, request):

        try:

            BackupService().create_backup()

            self.message_user(
                request,
                "نسخه پشتیبان با موفقیت ایجاد شد.",
                messages.SUCCESS,
            )

        except Exception as e:

            self.message_user(
                request,
                str(e),
                messages.ERROR,
            )

        return HttpResponseRedirect(
            reverse(
                "admin:app_backup_backup_changelist",
            )
        )

    ####################################################
    # Upload Backup ZIP
    ####################################################

    def upload_backup_view(self, request):

        if not request.user.is_superuser:
            self.message_user(
                request,
                "فقط مدیر سیستم مجاز است.",
                messages.ERROR,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:app_backup_backup_changelist",
                )
            )

        if request.method == "POST":

            uploaded_file = request.FILES.get(
                  "backup",
            )

            if uploaded_file is None:
                self.message_user(
                    request,
                    "فایلی انتخاب نشده است.",
                    messages.ERROR,
                )

                return HttpResponseRedirect(
                    request.path,
                )

            if not uploaded_file.name.lower().endswith(".zip"):
                self.message_user(
                    request,
                    "فقط فایل ZIP مجاز است.",
                    messages.ERROR,
                )

                return HttpResponseRedirect(
                    request.path,
                )

            storage = FileSystemStorage(
                location=BACKUP_DIRECTORY,
            )

            filename = storage.save(
                uploaded_file.name,
                uploaded_file,
            )

            file_path = BACKUP_DIRECTORY / filename

            sha256 = hashlib.sha256()

            with file_path.open("rb") as file:

                while chunk := file.read(8192):
                    sha256.update(chunk)

            Backup.objects.update_or_create(
                file_name=filename,
                defaults={
                    "file_size": file_path.stat().st_size,
                    "checksum": sha256.hexdigest(),
                },
            )

            self.message_user(
                request,
                "فایل با موفقیت بارگذاری شد.",
                messages.SUCCESS,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:app_backup_backup_changelist",
                )
            )

        return render(
            request,
            "admin/app_backup_upload.html",
        )

    ####################################################
    # Download
    ####################################################

    def download_backup_view(
        self,
        request,
        backup_id,
    ):

        backup = get_object_or_404(
            Backup,
            pk=backup_id,
        )

        if not backup.file_exists:

            self.message_user(
                request,
                "فایل نسخه پشتیبان وجود ندارد.",
                messages.ERROR,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:app_backup_backup_changelist",
                )
            )

        return FileResponse(
            backup.backup_path.open("rb"),
            as_attachment=True,
            filename=backup.file_name,
        )

    ####################################################
    # Restore
    ####################################################

    def restore_backup_view(
        self,
        request,
        backup_id,
    ):

        if not request.user.is_superuser:

            self.message_user(
                request,
                "فقط مدیر سیستم مجاز است.",
                messages.ERROR,
            )

            return HttpResponseRedirect(
                reverse(
                    "admin:app_backup_backup_changelist",
                )
            )

        backup = get_object_or_404(
            Backup,
            pk=backup_id,
        )

        try:

            BackupService().create_backup()

            RestoreService(
                backup,
            ).restore()

            self.message_user(
                request,
                "نسخه پشتیبان با موفقیت بازیابی شد.",
                messages.SUCCESS,
            )

        except Exception as e:

            self.message_user(
                request,
                str(e),
                messages.ERROR,
            )

        return HttpResponseRedirect(
            reverse(
                "admin:app_backup_backup_changelist",
            )
        )