from django.db import models


class Visit(models.Model):
    ip = models.GenericIPAddressField(
        db_index=True,
        verbose_name="IP"
    )

    path = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Page"
    )

    user_agent = models.CharField(
        max_length=300,
        blank=True,
        default="",
        verbose_name="User Agent"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name="Visit Time"
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "بازدید"
        verbose_name_plural = "بازدیدها"

    def __str__(self):
        return f"{self.ip} | {self.path}"