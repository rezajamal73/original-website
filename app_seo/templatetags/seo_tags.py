import json

from django import template
from django.templatetags.static import static

from app_seo.schema import generate_schema


register = template.Library()



def get_seo(context):

    return context.get("seo")



def default_site_title(context):

    site_info = context.get("site_info")

    if site_info:

        name = (
            f"{site_info.name_company_p1_fa} "
            f"{site_info.name_company_p2_fa}"
        )

        return name.strip()

    return ""



# =========================
# Title
# =========================

@register.simple_tag(takes_context=True)
def seo_title(context):

    seo = get_seo(context)

    if seo and seo.title:

        return seo.title

    return default_site_title(context)



# =========================
# Description
# =========================

@register.simple_tag(takes_context=True)
def seo_description(context):

    seo = get_seo(context)

    if seo and seo.description:

        return seo.description

    return ""



# =========================
# Keywords
# =========================

@register.simple_tag(takes_context=True)
def seo_keywords(context):

    seo = get_seo(context)

    if seo:

        return seo.keywords or ""

    return ""



# =========================
# Robots
# =========================

@register.simple_tag(takes_context=True)
def seo_robots(context):

    seo = get_seo(context)

    if seo:

        return seo.robots

    return "index,follow"



# =========================
# Canonical
# =========================

@register.simple_tag(takes_context=True)
def seo_canonical(context):

    request = context.get("request")

    seo = get_seo(context)


    if seo and seo.canonical:

        return seo.canonical


    if request:

        return request.build_absolute_uri(
            request.path
        )


    return ""



# =========================
# OG Image
# =========================

@register.simple_tag(takes_context=True)
def seo_og_image(context):

    seo = get_seo(context)


    if seo and seo.og_image:

        return seo.og_image.url


    request = context.get("request")


    if request:

        return request.build_absolute_uri(
            static("images/default-og.jpg")
        )


    return ""



# =========================
# Schema JSON-LD
# =========================

@register.simple_tag(takes_context=True)
def seo_schema(context):

    seo = get_seo(context)


    schema = generate_schema(
        seo
    )


    return json.dumps(
        schema,
        ensure_ascii=False,
        indent=2
    )