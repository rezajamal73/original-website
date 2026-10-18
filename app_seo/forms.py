
# app_seo/forms.py

from urllib.parse import urlsplit

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import SEOSetting


class SEOSettingAdminForm(forms.ModelForm):
    """
    SEO settings validation for Django Admin.

    - No database schema changes.
    - No automatic modification of existing records.
    - Legacy canonical URLs remain editable if unchanged.
    - New or changed canonical URLs are validated.
    """

    class Meta:
        model = SEOSetting
        fields = "__all__"

    @staticmethod
    def _allowed_hosts():
        hosts = {
            "nkavosh.com",
            "www.nkavosh.com",
        }

        site_url = getattr(
            settings,
            "SITE_URL",
            "",
        )

        if site_url:
            try:
                parsed = urlsplit(str(site_url))

                if parsed.hostname:
                    hosts.add(
                        parsed.hostname.lower()
                    )

            except ValueError:
                pass

        return hosts

    def clean_canonical(self):
        canonical = (
            self.cleaned_data.get("canonical") or ""
        ).strip()

        if not canonical:
            return ""

        # Existing records may contain canonical URLs
        # created before the new validation rules.
        # Preserve them when the field is unchanged.
        if self.instance and self.instance.pk:
            previous = (
                SEOSetting.objects.filter(
                    pk=self.instance.pk
                )
                .values_list(
                    "canonical",
                    flat=True,
                )
                .first()
            )

            if (previous or "").strip() == canonical:
                return canonical

        if any(
            ord(char) < 32
            for char in canonical
        ):
            raise ValidationError(
                "آدرس Canonical شامل نویسه نامعتبر است."
            )

        if "\\" in canonical:
            raise ValidationError(
                "آدرس Canonical نباید شامل بک‌اسلش باشد."
            )

        try:
            parsed = urlsplit(canonical)

            hostname = (
                parsed.hostname.lower()
                if parsed.hostname
                else ""
            )

            port = parsed.port

        except ValueError:
            raise ValidationError(
                "ساختار آدرس Canonical معتبر نیست."
            )

        if parsed.scheme.lower() != "https":
            raise ValidationError(
                "آدرس Canonical باید با https:// شروع شود."
            )

        if not hostname:
            raise ValidationError(
                "دامنه آدرس Canonical مشخص نیست."
            )

        if parsed.username or parsed.password:
            raise ValidationError(
                "وجود نام کاربری یا رمز در آدرس مجاز نیست."
            )

        if port not in (None, 443):
            raise ValidationError(
                "پورت آدرس Canonical مجاز نیست."
            )

        if hostname not in self._allowed_hosts():
            raise ValidationError(
                "آدرس Canonical باید متعلق به دامنه سایت باشد."
            )

        if parsed.fragment:
            raise ValidationError(
                "آدرس Canonical نباید شامل # باشد."
            )

        if parsed.query:
            raise ValidationError(
                "آدرس Canonical نباید دارای پارامترهای ? باشد."
            )

        return canonical

    def clean(self):
        cleaned_data = super().clean()

        publish_at = cleaned_data.get(
            "publish_at"
        )

        expire_at = cleaned_data.get(
            "expire_at"
        )

        if (
            publish_at is not None
            and expire_at is not None
            and expire_at <= publish_at
        ):
            self.add_error(
                "expire_at",
                "تاریخ انقضا باید بعد از تاریخ انتشار باشد.",
            )

        content_type = cleaned_data.get(
            "content_type"
        )

        page_key = (
            cleaned_data.get("page_key") or ""
        ).strip()

        app_label = (
            cleaned_data.get("app_label") or ""
        ).strip()

        model_name = (
            cleaned_data.get("model_name") or ""
        ).strip()

        object_id = cleaned_data.get(
            "object_id"
        )

        original = None

        if self.instance and self.instance.pk:
            original = (
                SEOSetting.objects.filter(
                    pk=self.instance.pk
                )
                .first()
            )

        # Do not block ordinary edits to historical
        # records because of unchanged old identifiers.
        identity_changed = original is None

        if original is not None:
            identity_changed = any((
                original.content_type != content_type,
                (original.page_key or "") != page_key,
                (original.app_label or "") != app_label,
                (original.model_name or "") != model_name,
                original.object_id != object_id,
            ))

        if identity_changed:
            if (
                content_type == "page"
                and not page_key
            ):
                self.add_error(
                    "page_key",
                    "برای صفحه ثابت، کلید صفحه الزامی است.",
                )

            has_object_reference = (
                bool(app_label)
                or bool(model_name)
                or object_id is not None
            )

            if has_object_reference:
                if not app_label:
                    self.add_error(
                        "app_label",
                        "نام اپلیکیشن را وارد کنید.",
                    )

                if not model_name:
                    self.add_error(
                        "model_name",
                        "نام مدل را وارد کنید.",
                    )

                if object_id is None:
                    self.add_error(
                        "object_id",
                        "شناسه محتوای مرتبط را وارد کنید.",
                    )

        # Duplicate checks are aligned with the
        # existing SEOSetting database constraints.
        if (
            app_label
            and model_name
            and object_id is not None
        ):
            duplicates = (
                SEOSetting.objects.filter(
                    app_label=app_label,
                    model_name=model_name,
                    object_id=object_id,
                )
            )

            if self.instance and self.instance.pk:
                duplicates = duplicates.exclude(
                    pk=self.instance.pk
                )

            if duplicates.exists():
                self.add_error(
                    "object_id",
                    "برای این محتوا قبلاً تنظیمات SEO ثبت شده است.",
                )

        if content_type == "page" and page_key:
            duplicates = (
                SEOSetting.objects.filter(
                    content_type="page",
                    page_key=page_key,
                )
            )

            if self.instance and self.instance.pk:
                duplicates = duplicates.exclude(
                    pk=self.instance.pk
                )

            if duplicates.exists():
                self.add_error(
                    "page_key",
                    "برای این کلید صفحه قبلاً تنظیمات SEO ثبت شده است.",
                )

        return cleaned_data
