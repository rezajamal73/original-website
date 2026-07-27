from decimal import Decimal
from uuid import UUID
from datetime import date, datetime, time, timedelta
import json
import sys

from django.db import connection
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models.fields.files import FieldFile
from django.utils import timezone

from app_log.middleware import get_current_request
from .models import SystemLog


def serialize_instance(instance):
    data = {}

    for field in instance._meta.get_fields():

        # فقط فیلدهای واقعی دیتابیس
        if not hasattr(field, "attname"):
            continue

        try:
            value = getattr(instance, field.name)

        except Exception:
            continue

        # فایل‌ها (تصویر، PDF، SVG، ویدئو و...)
        if isinstance(value, FieldFile):

            data[field.name] = (
                value.name
                if value
                else None
            )


        # ForeignKey
        elif hasattr(value, "_meta"):

            data[field.name] = (
                value.pk
                if value
                else None
            )


        # تاریخ و زمان
        elif isinstance(value, (datetime, date, time)):

            data[field.name] = value.isoformat()


        # Decimal
        elif isinstance(value, Decimal):

            data[field.name] = float(value)


        # UUID
        elif isinstance(value, UUID):

            data[field.name] = str(value)


        else:

            try:
                json.dumps(value)
                data[field.name] = value

            except Exception:
                data[field.name] = str(value)

    return data


def save_log(sender, instance, action):
    # جلوگیری از ثبت خود جدول لاگ
    if sender == SystemLog:
        return

    # جلوگیری از ثبت اپ‌های سیستمی Django
    if sender._meta.app_label in (
            "admin",
            "auth",
            "contenttypes",
            "sessions",
            "app_visit",  # عدم ثبت لاگ بازدیدها
    ):
        return

    # جلوگیری از ثبت هنگام migrate
    if "migrate" in sys.argv:
        return

    # جلوگیری از خطا قبل از ساخته شدن جدول لاگ
    if "app_log_systemlog" not in connection.introspection.table_names():
        return

    # --------------------------------
    # حذف فقط یک لاگ قدیمی‌تر از یک سال
    # --------------------------------

    expire_time = timezone.now() - timedelta(days=120)

    oldest_log = (
        SystemLog.objects
        .filter(created_at__lt=expire_time)
        .order_by("created_at")
        .first()
    )

    if oldest_log:
        oldest_log.delete()

    # --------------------------------
    # دریافت کاربر و IP
    # --------------------------------

    request = get_current_request()

    user = None
    ip = None

    if request:

        if (
                hasattr(request, "user")
                and request.user.is_authenticated
        ):
            user = request.user

        forwarded = request.META.get(
            "HTTP_X_FORWARDED_FOR"
        )

        if forwarded:

            ip = forwarded.split(",")[0].strip()

        else:

            ip = request.META.get(
                "REMOTE_ADDR"
            )

    # --------------------------------
    # نام امن اپلیکیشن
    # --------------------------------

    app_config = sender._meta.app_config

    if app_config:

        app_name = app_config.verbose_name

    else:

        app_name = sender._meta.app_label

    model_name = sender._meta.verbose_name

    # --------------------------------
    # ثبت لاگ
    # --------------------------------

    SystemLog.objects.create(

        app_name=app_name,

        model_name=model_name,

        object_id=instance.pk,

        object_name=str(instance),

        action=action,

        user=user,

        ip_address=ip,

        old_data=(
            serialize_instance(instance)
            if action == "delete"
            else None
        ),

        new_data=(
            serialize_instance(instance)
            if action != "delete"
            else None
        ),
    )


@receiver(
    post_save,
    dispatch_uid="app_log_post_save"
)
def log_create_update(sender, instance, created, **kwargs):
    save_log(

        sender=sender,

        instance=instance,

        action=(
            "create"
            if created
            else "update"
        ),
    )


@receiver(
    post_delete,
    dispatch_uid="app_log_post_delete"
)
def log_delete(sender, instance, **kwargs):
    save_log(

        sender=sender,

        instance=instance,

        action="delete",
    )
