# app_seo/templatetags/seo_tags.py

import json

from django import template
from django.templatetags.static import static

from app_seo.schema import generate_schema
from app_seo.analyzer import analyze


register = template.Library()


# =====================================================
#  کمک‌تابع‌ها
# =====================================================

def _get_seo(context):
    """
    اول از context، بعد از request.seo.
    """
    seo = context.get("seo")

    if seo:
        return seo

    request = context.get("request")

    if request:
        return getattr(request, "seo", None)

    return None


def _site_info(context):
    return context.get("site_info")


def _default_site_title(context):
    """عنوان پیش‌فرض سایت اگر SEO نداشتیم."""
    site_info = _site_info(context)

    if site_info:
        parts = [
            getattr(site_info, "name_company_p1_fa", "") or "",
            getattr(site_info, "name_company_p2_fa", "") or "",
        ]
        name = " ".join(p for p in parts if p).strip()
        if name:
            return name

    from django.conf import settings
    return getattr(settings, "SITE_NAME", "")


# =====================================================
#  Title
# =====================================================

@register.simple_tag(takes_context=True)
def seo_title(context):
    """عنوان SEO صفحه."""
    seo = _get_seo(context)

    if seo and getattr(seo, "title", None):
        return seo.title

    return _default_site_title(context)


# =====================================================
#  Description
# =====================================================

@register.simple_tag(takes_context=True)
def seo_description(context):
    """توضیحات SEO صفحه."""
    seo = _get_seo(context)

    if seo and getattr(seo, "description", None):
        return seo.description

    return ""


# =====================================================
#  Keywords
# =====================================================

@register.simple_tag(takes_context=True)
def seo_keywords(context):
    """کلمات کلیدی صفحه."""
    seo = _get_seo(context)

    if seo:
        return getattr(seo, "keywords", "") or ""

    return ""


# =====================================================
#  Robots
# =====================================================

@register.simple_tag(takes_context=True)
def seo_robots(context):
    """مقدار robots صفحه (index,follow یا noindex,nofollow)."""
    seo = _get_seo(context)

    if seo:
        return getattr(seo, "robots", "index,follow") or "index,follow"

    return "index,follow"


# =====================================================
#  Canonical
# =====================================================

@register.simple_tag(takes_context=True)
def seo_canonical(context):
    """آدرس canonical صفحه."""
    seo = _get_seo(context)

    if seo:
        canonical = getattr(seo, "canonical", None)
        if canonical:
            return canonical

    request = context.get("request")

    if request:
        try:
            return request.build_absolute_uri(request.path)
        except Exception:
            return ""

    return ""


# =====================================================
#  OG Image URL  —  هم SEOContext هم SEOSetting
# =====================================================

@register.simple_tag(takes_context=True)
def seo_og_image(context):
    """URL تصویر Open Graph."""
    seo = _get_seo(context)

    if seo:
        # SEOContext → property
        url = getattr(seo, "og_image_url", None)
        if url:
            return url

        # SEOSetting خام → فیلد ImageField
        image = getattr(seo, "og_image", None)
        if image:
            try:
                return image.url
            except Exception:
                pass

    request = context.get("request")

    if request:
        try:
            return request.build_absolute_uri(
                static("images/default-og.jpg")
            )
        except Exception:
            return ""

    return ""


# =====================================================
#  Schema JSON-LD
# =====================================================

@register.simple_tag(takes_context=True)
def seo_schema(context):
    """
    JSON-LD معتبر برای قرار گرفتن داخل <script type="application/ld+json">.
    """
    seo = _get_seo(context)

    # اول: اگر SEOContext است، schema_json_ld را بگیر
    if seo and hasattr(seo, "schema_json_ld"):
        result = seo.schema_json_ld
        if result:
            return result

    # fallback: خودمان generate کن
    schema = generate_schema(seo)

    try:
        return json.dumps(schema, ensure_ascii=False, indent=2)
    except (TypeError, ValueError):
        return "{}"


# =====================================================
#  Breadcrumb
# =====================================================

@register.simple_tag(takes_context=True)
def seo_breadcrumb(context):
    """
    HTML آماده Breadcrumb از SEOContext.breadcrumb.
    """
    seo = _get_seo(context)

    if seo is None:
        return ""

    items = getattr(seo, "breadcrumb", None)

    if not items:
        return ""

    html_parts = ['<nav aria-label="breadcrumb" class="seo-breadcrumb">']
    html_parts.append('<ol class="breadcrumb">')

    for item in items:
        label = item.get("label", "")
        url = item.get("url", "")
        is_current = item.get("is_current", False)

        if is_current or not url:
            html_parts.append(
                f'<li class="breadcrumb-item active" '
                f'aria-current="page">{label}</li>'
            )
        else:
            html_parts.append(
                f'<li class="breadcrumb-item">'
                f'<a href="{url}">{label}</a></li>'
            )

    html_parts.append("</ol>")
    html_parts.append("</nav>")

    return "".join(html_parts)


# =====================================================
#  Hreflang
# =====================================================

@register.simple_tag(takes_context=True)
def seo_hreflang(context):
    """
    تگ‌های <link rel="alternate"> برای hreflang.
    """
    seo = _get_seo(context)

    if seo is None:
        return ""

    items = getattr(seo, "hreflang", None)

    if not items:
        return ""

    lines = []

    for item in items:
        lang = item.get("lang", "")
        url = item.get("url", "")

        if not lang or not url:
            continue

        lines.append(
            f'<link rel="alternate" hreflang="{lang}" href="{url}">'
        )

    return "\n".join(lines)


# =====================================================
#  SEO Score
# =====================================================

@register.simple_tag(takes_context=True)
def seo_score(context):
    """نمایش امتیاز SEO با رنگ."""
    seo = _get_seo(context)

    if seo is None:
        return ""

    score = getattr(seo, "seo_score", 0) or 0

    if score >= 70:
        color = "#198754"
        label = "خوب"
    elif score >= 40:
        color = "#ffc107"
        label = "قابل بهبود"
    else:
        color = "#dc3545"
        label = "ضعیف"

    return (
        f'<span class="seo-score" '
        f'style="background:{color};color:#fff;'
        f'padding:4px 10px;border-radius:12px;'
        f'font-size:12px;font-weight:bold;">'
        f'{score} / 100 — {label}'
        f'</span>'
    )


# =====================================================
#  SEO Score Value
# =====================================================

@register.simple_tag(takes_context=True)
def seo_score_value(context):
    """فقط عدد امتیاز SEO."""
    seo = _get_seo(context)

    if seo is None:
        return 0

    return getattr(seo, "seo_score", 0) or 0


# =====================================================
#  SEO Analysis
# =====================================================

@register.simple_tag(takes_context=True)
def seo_analysis(context):
    """لیست HTML چک‌های تحلیل Yoast."""
    seo = _get_seo(context)

    if seo is None:
        return ""

    setting = getattr(seo, "setting", None) or seo

    try:
        result = analyze(setting, obj=getattr(seo, "obj", None))
    except Exception:
        return ""

    if not result:
        return ""

    checks = result.get("flat", [])

    if not checks:
        return ""

    html_parts = ['<ul class="seo-analysis-list">']

    for item in checks:
        icon = item.get("icon", "")
        message = item.get("message", "")

        html_parts.append(
            f'<li>{icon} {message}</li>'
        )

    html_parts.append("</ul>")

    return "".join(html_parts)


# =====================================================
#  Google Preview
# =====================================================

@register.simple_tag(takes_context=True)
def seo_google_preview(context):
    """HTML پیش‌نمایش گوگل (برای پنل یا debug)."""
    seo = _get_seo(context)

    if seo is None:
        return ""

    title = getattr(seo, "title", "") or ""
    description = getattr(seo, "description", "") or ""
    url = getattr(seo, "canonical", "") or ""

    title = title[:60] + ("…" if len(title) > 60 else "")
    description = description[:160] + ("…" if len(description) > 160 else "")

    return (
        f'<div class="seo-google-preview" '
        f'style="max-width:600px;padding:14px 16px;'
        f'border:1px solid #dadce0;border-radius:10px;background:#fff;">'
        f'<div style="color:#5f6368;font-size:12px;">{url}</div>'
        f'<div style="color:#1a0dab;font-size:18px;line-height:1.3;">{title}</div>'
        f'<div style="color:#4d5156;font-size:13px;line-height:1.5;">{description}</div>'
        f'</div>'
    )


# =====================================================
#  Twitter Card
# =====================================================

@register.simple_tag(takes_context=True)
def seo_twitter_card(context):
    """تگ‌های کامل Twitter Card."""
    seo = _get_seo(context)

    if seo is None:
        return ""

    lines = []

    card = getattr(seo, "twitter_card", "summary_large_image") or "summary_large_image"
    lines.append(f'<meta name="twitter:card" content="{card}">')

    title = (
        getattr(seo, "twitter_title", None)
        or getattr(seo, "og_title", None)
    )
    if title:
        lines.append(f'<meta name="twitter:title" content="{title}">')

    description = (
        getattr(seo, "twitter_description", None)
        or getattr(seo, "og_description", None)
    )
    if description:
        lines.append(
            f'<meta name="twitter:description" content="{description}">'
        )

    image = (
        getattr(seo, "twitter_image_url", None)
        or getattr(seo, "og_image_url", None)
    )
    if image:
        lines.append(f'<meta name="twitter:image" content="{image}">')

    return "\n".join(lines)


# =====================================================
#  Open Graph
# =====================================================

@register.simple_tag(takes_context=True)
def seo_og(context):
    """تگ‌های کامل Open Graph."""
    seo = _get_seo(context)

    if seo is None:
        return ""

    lines = []

    og_type = getattr(seo, "og_type", "website") or "website"
    lines.append(f'<meta property="og:type" content="{og_type}">')

    title = getattr(seo, "og_title", None) or getattr(seo, "title", None)
    if title:
        lines.append(f'<meta property="og:title" content="{title}">')

    description = (
        getattr(seo, "og_description", None)
        or getattr(seo, "description", None)
    )
    if description:
        lines.append(
            f'<meta property="og:description" content="{description}">'
        )

    canonical = getattr(seo, "canonical", None)
    if canonical:
        lines.append(f'<meta property="og:url" content="{canonical}">')

    image = getattr(seo, "og_image_url", None)
    if image:
        lines.append(f'<meta property="og:image" content="{image}">')

    return "\n".join(lines)


# =====================================================
#  Meta Robots Tag
# =====================================================

@register.simple_tag(takes_context=True)
def seo_meta_robots(context):
    """تگ <meta name="robots">."""
    robots = seo_robots(context)

    if not robots:
        return ""

    return f'<meta name="robots" content="{robots}">'


# =====================================================
#  Meta Description Tag
# =====================================================

@register.simple_tag(takes_context=True)
def seo_meta_description(context):
    """تگ <meta name="description">."""
    description = seo_description(context)

    if not description:
        return ""

    return f'<meta name="description" content="{description}">'


# =====================================================
#  Meta Keywords Tag
# =====================================================

@register.simple_tag(takes_context=True)
def seo_meta_keywords(context):
    """تگ <meta name="keywords">."""
    keywords = seo_keywords(context)

    if not keywords:
        return ""

    return f'<meta name="keywords" content="{keywords}">'


# =====================================================
#  Canonical Tag
# =====================================================

@register.simple_tag(takes_context=True)
def seo_canonical_tag(context):
    """تگ <link rel="canonical">."""
    canonical = seo_canonical(context)

    if not canonical:
        return ""

    return f'<link rel="canonical" href="{canonical}">'