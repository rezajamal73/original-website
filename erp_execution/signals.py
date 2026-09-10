from django.db.models.signals import post_save
from django.dispatch import receiver

from erp_requests.models import Request
from .models import Execution


@receiver(post_save, sender=Request)
def create_execution_for_request(
    sender,
    instance,
    created,
    **kwargs
):
    if created:

        Execution.objects.get_or_create(
            request=instance,
            defaults={
                "executor": instance.requester,
            }
        )