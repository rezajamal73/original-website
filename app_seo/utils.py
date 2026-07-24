from django.contrib.contenttypes.models import ContentType

from .models import SEOSetting



class SEOManager:


    @staticmethod
    def get_page(page_key):

        return (
            SEOSetting.objects
            .filter(
                content_type="page",
                page_key=page_key,
                is_active=True,
            )
            .first()
        )



    @staticmethod
    def get_object(instance):
        if not instance:
            return None

        content_type = ContentType.objects.get_for_model(
            instance.__class__
        )

        return (
            SEOSetting.objects
            .filter(
                app_label=content_type.app_label,
                model_name=content_type.model,
                object_id=instance.pk,
                is_active=True,
            )
            .first()
        )



    @staticmethod
    def get_by_id(
        app_label,
        model_name,
        object_id
    ):

        return (
            SEOSetting.objects
            .filter(
                app_label=app_label,
                model_name=model_name,
                object_id=object_id,
                is_active=True,
            )
            .first()
        )