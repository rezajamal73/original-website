
import os
import sys
import fcntl
import shutil
import sqlite3
import zipfile

from datetime import datetime
from pathlib import Path, PurePosixPath

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "original_website.setting.prod",
)

import django
django.setup()

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connections

from app_backup.models import Backup
from app_backup.restore_service import RestoreService


class Command(BaseCommand):

    help = (
        "بررسی و بازیابی آفلاین بکاپ؛ "
        "فقط Media یا Media همراه دیتابیس"
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "backup_id",
            type=int,
            help="شناسه نسخه پشتیبان",
        )

        parser.add_argument(
            "--media-only",
            action="store_true",
            help="بازیابی فقط Media بدون تغییر دیتابیس",
        )

        parser.add_argument(
            "--confirm",
            action="store_true",
            help="تأیید اجرای بازیابی واقعی",
        )

        parser.add_argument(
            "--offline-verified",
            action="store_true",
            help="تأیید توقف سایت و تمام پردازش‌های نویسنده",
        )

    def handle(self, *args, **options):

        backup_id = options["backup_id"]
        media_only = options["media_only"]
        confirmed = options["confirm"]
        offline_verified = options["offline_verified"]

        try:
            backup = Backup.objects.get(pk=backup_id)
        except Backup.DoesNotExist:
            raise CommandError(
                f"بکاپ شماره {backup_id} پیدا نشد."
            )

        mode = (
            "فقط Media"
            if media_only
            else "Media + Database"
        )

        self.stdout.write(
            f"بکاپ: {backup.file_name}"
        )
        self.stdout.write(
            f"حالت انتخاب‌شده: {mode}"
        )

        service = RestoreService(backup)

        try:
            result = service.restore()
        except Exception as exc:
            raise CommandError(
                f"اعتبارسنجی بکاپ ناموفق بود: {exc}"
            ) from exc

        if not result.get("valid"):
            raise CommandError(
                "سلامت بکاپ تأیید نشد."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "سلامت بکاپ تأیید شد."
            )
        )

        if not confirmed:
            self.stdout.write(
                self.style.WARNING(
                    "فقط بررسی انجام شد؛ "
                    "هیچ اطلاعاتی جایگزین نشده است."
                )
            )
            return

        if not offline_verified:
            raise CommandError(
                "بازیابی واقعی نیازمند توقف سایت، "
                "کرون‌ها و همه پردازش‌های نویسنده است. "
                "پس از بررسی توقف آن‌ها، "
                "--offline-verified را اضافه کنید."
            )

        if (
            settings.DATABASES["default"]["ENGINE"]
            != "django.db.backends.sqlite3"
        ):
            raise CommandError(
                "فقط SQLite پشتیبانی می‌شود."
            )

        database = Path(
            settings.DATABASES["default"]["NAME"]
        ).absolute()

        media = Path(
            settings.MEDIA_ROOT
        ).absolute()

        if not database.is_file() or database.is_symlink():
            raise CommandError(
                "مسیر دیتابیس فعلی نامعتبر است."
            )

        if not media.is_dir() or media.is_symlink():
            raise CommandError(
                "مسیر Media فعلی نامعتبر است."
            )

        if database.resolve() == media.resolve():
            raise CommandError(
                "مسیر دیتابیس و Media یکسان است."
            )

        recovery_root = (
            database.parent / "restore_recovery"
        )

        recovery_root.mkdir(
            mode=0o700,
            parents=True,
            exist_ok=True,
        )

        lock_path = recovery_root / ".restore.lock"

        with lock_path.open("a+") as lock:

            try:
                fcntl.flock(
                    lock,
                    fcntl.LOCK_EX | fcntl.LOCK_NB,
                )
            except BlockingIOError:
                raise CommandError(
                    "عملیات بازیابی دیگری در حال اجراست."
                )

            # پس از گرفتن قفل دوباره وضعیت SQLite
            # بررسی می‌شود.
            for suffix in ("-wal", "-shm", "-journal"):

                sidecar = Path(
                    str(database) + suffix
                )

                if sidecar.exists():
                    raise CommandError(
                        "فایل جانبی SQLite وجود دارد: "
                        f"{sidecar}. "
                        "تا بررسی و توقف کامل پردازش‌ها "
                        "بازیابی مجاز نیست."
                    )

            self.perform_restore(
                backup=backup,
                database=database,
                media=media,
                recovery_root=recovery_root,
                media_only=media_only,
            )

    def perform_restore(
        self,
        backup,
        database,
        media,
        recovery_root,
        media_only,
    ):

        run_directory = recovery_root / (
            "run_"
            + datetime.now().strftime(
                "%Y%m%d_%H%M%S_%f"
            )
        )

        run_directory.mkdir(mode=0o700)

        staged_media = (
            run_directory / "staged_media"
        )

        staged_media.mkdir()

        staged_database = (
            run_directory / "staged.sqlite3"
        )

        saved_database = (
            run_directory / "original.sqlite3"
        )

        saved_media = (
            run_directory / "original_media"
        )

        failed_media = (
            run_directory / "failed_restored_media"
        )

        media_moved = False
        database_replaced = False

        self.stdout.write(
            f"پوشه نسخه نجات: {run_directory}"
        )

        try:

            self.stdout.write(
                "در حال آماده‌سازی فایل‌های Media..."
            )

            service = RestoreService(backup)

            with zipfile.ZipFile(
                backup.backup_path,
                "r",
            ) as archive:

                members = service._validate_zip(
                    archive
                )

                media_members = [
                    item
                    for item in members
                    if (
                        item.filename.startswith("Media/")
                        and not item.is_dir()
                    )
                ]

                if not media_members:
                    raise RuntimeError(
                        "هیچ فایل Media در بکاپ وجود ندارد. "
                        "برای جلوگیری از حذف ناخواسته "
                        "Media فعلی، عملیات متوقف شد."
                    )

                for member in media_members:

                    relative = PurePosixPath(
                        member.filename
                    ).relative_to("Media")

                    if not relative.parts:
                        continue

                    target = staged_media.joinpath(
                        *relative.parts
                    )

                    target.parent.mkdir(
                        parents=True,
                        exist_ok=True,
                    )

                    with archive.open(
                        member,
                        "r",
                    ) as source:

                        with target.open(
                            "xb"
                        ) as destination:

                            shutil.copyfileobj(
                                source,
                                destination,
                                length=1024 * 1024,
                            )

                self.stdout.write(
                    f"{len(media_members)} فایل Media "
                    "آماده شد."
                )

                if not media_only:

                    self.stdout.write(
                        "در حال آماده‌سازی دیتابیس بکاپ..."
                    )

                    database_members = [
                        item
                        for item in members
                        if (
                            item.filename
                            == "Database/db.sqlite3"
                            and not item.is_dir()
                        )
                    ]

                    if len(database_members) != 1:
                        raise RuntimeError(
                            "فایل دیتابیس مورد انتظار "
                            "در بکاپ پیدا نشد."
                        )

                    with archive.open(
                        database_members[0],
                        "r",
                    ) as source:

                        with staged_database.open(
                            "xb"
                        ) as destination:

                            shutil.copyfileobj(
                                source,
                                destination,
                                length=1024 * 1024,
                            )

                    RestoreService._verify_sqlite(
                        staged_database
                    )

            # مجوزهای پوشه Media حفظ می‌شود.
            original_media_mode = (
                media.stat().st_mode & 0o777
            )

            staged_media.chmod(
                original_media_mode
            )

            if not media_only:

                self.stdout.write(
                    "در حال تهیه نسخه نجات از دیتابیس فعلی..."
                )

                connections.close_all()

                # mode=rw مانع ساخت تصادفی دیتابیس می‌شود.
                source_uri = (
                    database.resolve().as_uri()
                    + "?mode=rw"
                )

                source = sqlite3.connect(
                    source_uri,
                    uri=True,
                    timeout=10,
                )

                destination = sqlite3.connect(
                    str(saved_database),
                    timeout=10,
                )

                try:
                    source.backup(destination)
                finally:
                    destination.close()
                    source.close()

                RestoreService._verify_sqlite(
                    saved_database
                )

                staged_database.chmod(
                    database.stat().st_mode & 0o777
                )

                # هیچ فایل جانبی نباید هنگام جایگزینی
                # دیتابیس باقی مانده باشد.
                for suffix in (
                    "-wal",
                    "-shm",
                    "-journal",
                ):
                    if Path(
                        str(database) + suffix
                    ).exists():
                        raise RuntimeError(
                            "فایل جانبی SQLite ایجاد شده است؛ "
                            "احتمال وجود پردازش فعال وجود دارد."
                        )

            # انتقال Media فعلی به پوشه نجات.
            self.stdout.write(
                "در حال انتقال Media فعلی به نسخه نجات..."
            )

            media.rename(saved_media)
            media_moved = True

            # انتقال Media استخراج‌شده به محل اصلی.
            staged_media.rename(media)

            if not media_only:

                self.stdout.write(
                    "در حال جایگزینی دیتابیس..."
                )

                connections.close_all()

                os.replace(
                    staged_database,
                    database,
                )

                database_replaced = True

                RestoreService._verify_sqlite(
                    database
                )

            if media_only:

                self.stdout.write(
                    self.style.SUCCESS(
                        "بازیابی فقط Media با موفقیت "
                        "انجام شد. دیتابیس تغییر نکرد."
                    )
                )

            else:

                self.stdout.write(
                    self.style.SUCCESS(
                        "بازیابی Media و Database "
                        "با موفقیت انجام شد."
                    )
                )

            self.stdout.write(
                "نسخه نجات اطلاعات قبلی:"
            )

            self.stdout.write(
                str(run_directory)
            )

            self.stdout.write(
                self.style.WARNING(
                    "نسخه نجات را حذف نکنید. "
                    "پیش از راه‌اندازی سایت، "
                    "وضعیت فایل‌ها و دیتابیس را "
                    "بررسی کنید."
                )
            )

        except Exception as exc:

            rollback_errors = []

            self.stderr.write(
                self.style.ERROR(
                    f"خطا در بازیابی: {exc}"
                )
            )

            if database_replaced:

                try:

                    rollback_temp = (
                        run_directory
                        / "rollback_database.sqlite3"
                    )

                    shutil.copy2(
                        saved_database,
                        rollback_temp,
                    )

                    os.replace(
                        rollback_temp,
                        database,
                    )

                    RestoreService._verify_sqlite(
                        database
                    )

                except Exception as error:

                    rollback_errors.append(
                        "بازگشت دیتابیس ناموفق بود: "
                        f"{error}"
                    )

            if media_moved:

                try:

                    if media.exists():

                        media.rename(
                            failed_media
                        )

                    saved_media.rename(
                        media
                    )

                except Exception as error:

                    rollback_errors.append(
                        "بازگشت Media ناموفق بود: "
                        f"{error}"
                    )

            self.stderr.write(
                f"مسیر نسخه نجات: {run_directory}"
            )

            if rollback_errors:

                for error in rollback_errors:
                    self.stderr.write(
                        self.style.ERROR(error)
                    )

                raise CommandError(
                    "بازیابی ناموفق بود و بازگشت اضطراری "
                    "نیز کامل انجام نشد. "
                    "سایت را روشن نکنید؛ "
                    "ابتدا وضعیت اطلاعات بررسی شود."
                ) from exc

            raise CommandError(
                "بازیابی ناموفق بود. "
                "بازگشت اضطراری تا حد امکان انجام شد. "
                "پیش از روشن‌کردن سایت، "
                "سلامت اطلاعات را بررسی کنید."
            ) from exc


if __name__ == "__main__":

    Command().run_from_argv(
        [
            sys.argv[0],
            "restore_backup_offline",
            *sys.argv[1:],
        ]
    )
