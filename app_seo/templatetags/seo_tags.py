
# app_seo/templatetags/seo_tags.py

import json
import re
from urllib.parse import urlsplit

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join

from app_seo.schema import generate_schema
from app_seo.analyzer import analyze


register = template.Library()


# =====================================================
# Helpers
# =====================================================

def _get_seo(context):
    seo = context.get("seo")
    if seo:
        return seo

    request = context.get("request")
    return getattr(request, "seo", None) if request else None


def _site_info(context):
    return context.get("site_info")


def _is_english_page(context):
    request = context.get("request")
    path = getattr(request, "path", "") if request else ""
    return path == "/en" or path.startswith("/en/")


def _default_site_title(context):
    site_info = _site_info(context)

    if site_info:
        suffix = "en" if _is_english_page(context) else "fa"

        parts = [
            getattr(
                site_info,
                "name_company_p1_" + suffix,
                "",
            ) or "",
            getattr(
                site_info,
                "name_company_p2_" + suffix,
                "",
            ) or "",
        ]

        name = " ".join(
            part for part in parts if part
        ).strip()

        if name:
            return name

    return getattr(settings, "SITE_NAME", "")


def _origin():
    raw = str(
        getattr(
            settings,
            "SITE_URL",
            "",
        ) or "https://nkavosh.com"
    ).strip()

    try:
        parts = urlsplit(raw)

        if (
            parts.scheme == "https"
            and parts.hostname in (
                "nkavosh.com",
                "www.nkavosh.com",
            )
            and not parts.username
            and not parts.password
        ):
            return "https://" + parts.netloc

    except ValueError:
        pass

    return "https://nkavosh.com"


def _valid_url(value, allow_relative=True):
    if not isinstance(value, str):
        return ""

    value = value.strip()

    if (
        not value
        or any(ord(char) < 32 for char in value)
        or "\\" in value
        or value.startswith("//")
    ):
        return ""

    try:
        parts = urlsplit(value)
    except ValueError:
        return ""

    if parts.scheme or parts.netloc:
        if (
            parts.scheme != "https"
            or parts.hostname not in (
                "nkavosh.com",
                "www.nkavosh.com",
            )
            or parts.username
            or parts.password
        ):
            return ""

        return value

    if (
        allow_relative
        and value.startswith("/")
        and not value.startswith("//")
    ):
        return _origin() + value

    return ""


def _items(seo, attribute):
    value = (
        getattr(seo, attribute, None)
        if seo
        else None
    )

    return (
        value
        if isinstance(value, (list, tuple))
        else []
    )


def _item_value(item, key, default=""):
    if isinstance(item, dict):
        return item.get(key, default)

    return getattr(item, key, default)


# =====================================================
# Title
# =====================================================

@register.simple_tag(takes_context=True)
def seo_title(context):
    seo = _get_seo(context)

    return (
        getattr(seo, "title", None)
        if seo
        else None
    ) or _default_site_title(context)


@register.simple_tag(takes_context=True)
def seo_title_en(context):
    seo = _get_seo(context)

    if seo is None:
        return _default_site_title(context)

    setting = getattr(
        seo,
        "setting",
        None,
    ) or seo

    obj = getattr(seo, "obj", None)

    fields = (
        (setting, "title_en"),
        (obj, "title_en"),
        (setting, "title"),
        (obj, "title_fa"),
    )

    for source, field in fields:
        value = (
            getattr(source, field, None)
            if source is not None
            else None
        )

        if value and str(value).strip():
            return value

    return _default_site_title(context)


# =====================================================
# Description
# =====================================================

@register.simple_tag(takes_context=True)
def seo_description(context):
    seo = _get_seo(context)

    return (
        getattr(seo, "description", "")
        if seo
        else ""
    ) or ""


@register.simple_tag(takes_context=True)
def seo_description_en(context):
    seo = _get_seo(context)

    if seo is None:
        return ""

    setting = getattr(
        seo,
        "setting",
        None,
    ) or seo

    obj = getattr(seo, "obj", None)

    fields = (
        (setting, "description_en"),
        (obj, "description_en"),
        (setting, "description"),
        (obj, "description_fa"),
        (obj, "description"),
    )

    for source, field in fields:
        value = (
            getattr(source, field, None)
            if source is not None
            else None
        )

        if value and str(value).strip():
            return value

    return ""


# =====================================================
# Keywords and Robots
# =====================================================

@register.simple_tag(takes_context=True)
def seo_keywords(context):
    seo = _get_seo(context)

    return (
        getattr(seo, "keywords", "")
        if seo
        else ""
    ) or ""


@register.simple_tag(takes_context=True)
def seo_robots(context):
    seo = _get_seo(context)

    return (
        getattr(seo, "robots", "")
        if seo
        else ""
    ) or "index,follow"


# =====================================================
# Canonical
# =====================================================

@register.simple_tag(takes_context=True)
def seo_canonical(context):
    seo = _get_seo(context)

    canonical = (
        getattr(seo, "canonical", None)
        if seo
        else None
    )

    url = (
        _valid_url(canonical)
        if canonical
        else ""
    )

    if url:
        return url

    request = context.get("request")

    path = (
        getattr(request, "path", "")
        if request
        else ""
    )

    return _valid_url(path) if path else ""


# =====================================================
# OG Image
# =====================================================

@register.simple_tag(takes_context=True)
def seo_og_image(context):
    seo = _get_seo(context)

    if seo:
        url = getattr(
            seo,
            "og_image_url",
            None,
        )

        if url:
            return _valid_url(str(url))

        image = getattr(
            seo,
            "og_image",
            None,
        )

        if image:
            try:
                return _valid_url(
                    str(image.url)
                )
            except (ValueError, OSError):
                pass

    return _valid_url(
        static("images/default-og.jpg")
    )


# =====================================================
# Schema JSON-LD
# =====================================================

@register.simple_tag(takes_context=True)
def seo_schema(context):
    seo = _get_seo(context)

    if (
        seo
        and hasattr(
            seo,
            "schema_json_ld",
        )
    ):
        result = seo.schema_json_ld

        if result:
            return result

    try:
        schema = generate_schema(seo)

        return json.dumps(
            schema,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )

    except (
        TypeError,
        ValueError,
        OverflowError,
    ):
        return "{}"


# =====================================================
# Breadcrumb
# =====================================================

@register.simple_tag(takes_context=True)
def seo_breadcrumb(context):
    items = _items(
        _get_seo(context),
        "breadcrumb",
    )

    if not items:
        return ""

    fragments = []

    for item in items:
        label = _item_value(
            item,
            "label",
        )

        url = _valid_url(
            _item_value(item, "url")
        )

        current = _item_value(
            item,
            "is_current",
            False,
        )

        if current or not url:
            fragments.append(
                format_html(
                    '<li class="breadcrumb-item active" '
                    'aria-current="page">{}</li>',
                    label,
                )
            )
        else:
            fragments.append(
                format_html(
                    '<li class="breadcrumb-item">'
                    '<a href="{}">{}</a></li>',
                    url,
                    label,
                )
            )

    content = format_html_join(
        "",
        "{}",
        ((part,) for part in fragments),
    )

    return format_html(
        '<nav aria-label="breadcrumb" '
        'class="seo-breadcrumb">'
        '<ol class="breadcrumb">{}</ol>'
        '</nav>',
        content,
    )


# =====================================================
# Hreflang
# =====================================================

@register.simple_tag(takes_context=True)
def seo_hreflang(context):
    items = _items(
        _get_seo(context),
        "hreflang",
    )

    lines = []

    for item in items:
        lang = str(
            _item_value(
                item,
                "lang",
            ) or ""
        ).strip()

        url = _valid_url(
            _item_value(
                item,
                "url",
            )
        )

        valid_lang = re.fullmatch(
            r"[A-Za-z]{2,3}"
            r"(?:-[A-Za-z0-9]{2,8})*"
            r"|x-default",
            lang,
        )

        if lang and valid_lang and url:
            lines.append(
                format_html(
                    '<link rel="alternate" '
                    'hreflang="{}" href="{}">',
                    lang,
                    url,
                )
            )

    if not lines:
        return ""

    return format_html_join(
        "\n",
        "{}",
        ((line,) for line in lines),
    )


# =====================================================
# SEO Score
# =====================================================

@register.simple_tag(takes_context=True)
def seo_score_value(context):
    seo = _get_seo(context)

    try:
        score = int(
            getattr(
                seo,
                "seo_score",
                0,
            ) or 0
        )

        return max(
            0,
            min(100, score),
        )

    except (TypeError, ValueError):
        return 0


@register.simple_tag(takes_context=True)
def seo_score(context):
    if _get_seo(context) is None:
        return ""

    score = seo_score_value(context)

    if score >= 70:
        color = "#198754"
        label = "خوب"

    elif score >= 40:
        color = "#ffc107"
        label = "قابل بهبود"

    else:
        color = "#dc3545"
        label = "ضعیف"

    return format_html(
        '<span class="seo-score" '
        'style="background:{};color:#fff;'
        'padding:4px 10px;border-radius:12px;'
        'font-size:12px;font-weight:bold;">'
        '{} / 100 — {}</span>',
        color,
        score,
        label,
    )


# =====================================================
# SEO Analysis
# =====================================================

@register.simple_tag(takes_context=True)
def seo_analysis(context):
    seo = _get_seo(context)

    if seo is None:
        return ""

    setting = getattr(
        seo,
        "setting",
        None,
    ) or seo

    try:
        result = analyze(
            setting,
            obj=getattr(
                seo,
                "obj",
                None,
            ),
        )

    except Exception:
        return ""

    checks = (
        result.get("flat", [])
        if isinstance(result, dict)
        else []
    )

    if not checks:
        return ""

    lines = []

    for item in checks:
        lines.append(
            format_html(
                "<li>{} {}</li>",
                _item_value(
                    item,
                    "icon",
                ),
                _item_value(
                    item,
                    "message",
                ),
            )
        )

    content = format_html_join(
        "",
        "{}",
        ((line,) for line in lines),
    )

    return format_html(
        '<ul class="seo-analysis-list">'
        '{}</ul>',
        content,
    )


# =====================================================
# Google Preview
# =====================================================

@register.simple_tag(takes_context=True)
def seo_google_preview(context):
    seo = _get_seo(context)

    if seo is None:
        return ""

    title = str(
        getattr(
            seo,
            "title",
            "",
        ) or ""
    )

    description = str(
        getattr(
            seo,
            "description",
            "",
        ) or ""
    )

    title = title[:60] + (
        "…" if len(title) > 60 else ""
    )

    description = description[:160] + (
        "…" if len(description) > 160 else ""
    )

    url = seo_canonical(context)

    return format_html(
        '<div class="seo-google-preview" '
        'style="max-width:600px;'
        'padding:14px 16px;'
        'border:1px solid #dadce0;'
        'border-radius:10px;'
        'background:#fff;">'
        '<div style="color:#5f6368;'
        'font-size:12px;">{}</div>'
        '<div style="color:#1a0dab;'
        'font-size:18px;line-height:1.3;">'
        '{}</div>'
        '<div style="color:#4d5156;'
        'font-size:13px;line-height:1.5;">'
        '{}</div>'
        '</div>',
        url,
        title,
        description,
    )


# =====================================================
# Twitter Card
# =====================================================

@register.simple_tag(takes_context=True)
def seo_twitter_card(context):
    seo = _get_seo(context)

    if seo is None:
        return ""

    lines = [
        format_html(
            '<meta name="twitter:card" '
            'content="{}">',
            getattr(
                seo,
                "twitter_card",
                None,
            ) or "summary_large_image",
        )
    ]

    values = (
        (
            "twitter:title",
            getattr(
                seo,
                "twitter_title",
                None,
            ) or getattr(
                seo,
                "og_title",
                None,
            ),
        ),
        (
            "twitter:description",
            getattr(
                seo,
                "twitter_description",
                None,
            ) or getattr(
                seo,
                "og_description",
                None,
            ),
        ),
        (
            "twitter:image",
            _valid_url(
                getattr(
                    seo,
                    "twitter_image_url",
                    None,
                ) or getattr(
                    seo,
                    "og_image_url",
                    None,
                )
            ),
        ),
    )

    for name, value in values:
        if value:
            lines.append(
                format_html(
                    '<meta name="{}" '
                    'content="{}">',
                    name,
                    value,
                )
            )

    return format_html_join(
        "\n",
        "{}",
        ((line,) for line in lines),
    )


# =====================================================
# Open Graph
# =====================================================

@register.simple_tag(takes_context=True)
def seo_og(context):
    seo = _get_seo(context)

    if seo is None:
        return ""

    lines = [
        format_html(
            '<meta property="og:type" '
            'content="{}">',
            getattr(
                seo,
                "og_type",
                None,
            ) or "website",
        )
    ]

    values = (
        (
            "og:title",
            getattr(
                seo,
                "og_title",
                None,
            ) or getattr(
                seo,
                "title",
                None,
            ),
        ),
        (
            "og:description",
            getattr(
                seo,
                "og_description",
                None,
            ) or getattr(
                seo,
                "description",
                None,
            ),
        ),
        (
            "og:url",
            seo_canonical(context),
        ),
        (
            "og:image",
            _valid_url(
                getattr(
                    seo,
                    "og_image_url",
                    None,
                )
            ),
        ),
    )

    for name, value in values:
        if value:
            lines.append(
                format_html(
                    '<meta property="{}" '
                    'content="{}">',
                    name,
                    value,
                )
            )

    return format_html_join(
        "\n",
        "{}",
        ((line,) for line in lines),
    )


# =====================================================
# Individual Meta Tags
# =====================================================

@register.simple_tag(takes_context=True)
def seo_meta_robots(context):
    robots = seo_robots(context)

    if not robots:
        return ""

    return format_html(
        '<meta name="robots" content="{}">',
        robots,
    )


@register.simple_tag(takes_context=True)
def seo_meta_description(context):
    description = seo_description(context)

    if not description:
        return ""

    return format_html(
        '<meta name="description" '
        'content="{}">',
        description,
    )


@register.simple_tag(takes_context=True)
def seo_meta_keywords(context):
    keywords = seo_keywords(context)

    if not keywords:
        return ""

    return format_html(
        '<meta name="keywords" '
        'content="{}">',
        keywords,
    )


@register.simple_tag(takes_context=True)
def seo_canonical_tag(context):
    canonical = seo_canonical(context)

    if not canonical:
        return ""

    return format_html(
        '<link rel="canonical" href="{}">',
        canonical,
    )
