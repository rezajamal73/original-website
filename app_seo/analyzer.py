
# app_seo/analyzer.py

import re
from html import unescape
from urllib.parse import urlsplit

from django.conf import settings
from django.utils.html import strip_tags


# =====================================================
# Helpers
# =====================================================

def _get(obj, *names, default=None):
    if obj is None:
        return default

    for name in names:
        try:
            value = getattr(obj, name, None)
        except (AttributeError, ValueError):
            continue

        if value is not None and value != "":
            return value

    return default


def _normalize(text):
    if not text:
        return ""

    value = unescape(str(text)).casefold()
    value = value.replace("\u200c", " ")
    value = value.replace("ي", "ی").replace("ك", "ک")

    return re.sub(r"\s+", " ", value).strip()


def _word_count(text):
    return len(_normalize(text).split())


def _phrase_pattern(keyphrase):
    phrase = _normalize(keyphrase)

    if not phrase:
        return None

    escaped = re.escape(phrase).replace(
        r"\ ", r"\s+"
    )

    return re.compile(
        r"(?<!\w)" + escaped + r"(?!\w)",
        re.UNICODE,
    )


def _contains_keyphrase(text, keyphrase):
    pattern = _phrase_pattern(keyphrase)

    return bool(
        pattern and pattern.search(_normalize(text))
    )


def _count_keyphrase(text, keyphrase):
    pattern = _phrase_pattern(keyphrase)

    if not pattern:
        return 0

    return len(
        pattern.findall(_normalize(text))
    )


def _keyphrase_density(text, keyphrase):
    words = _word_count(text)

    if not words:
        return 0.0

    occurrences = _count_keyphrase(
        text, keyphrase
    )

    phrase_words = _word_count(keyphrase)

    return (
        100.0
        * occurrences
        * phrase_words
        / words
    )


def _strip_html(text):
    if not text:
        return ""

    return unescape(strip_tags(str(text)))


# =====================================================
# Result types
# =====================================================

def _good(message):
    return {
        "status": "good",
        "message": message,
        "icon": "🟢",
    }


def _improvement(message):
    return {
        "status": "improvement",
        "message": message,
        "icon": "🟡",
    }


def _problem(message):
    return {
        "status": "problem",
        "message": message,
        "icon": "🔴",
    }


# =====================================================
# Keyphrase checks
# =====================================================

def _check_keyphrase_presence(seo, keyphrase):
    if keyphrase:
        return []

    return [
        _problem(
            "عبارت کلیدی اصلی تعیین نشده است."
        )
    ]


def _check_keyphrase_in_title(seo, keyphrase):
    title = _get(seo, "title") or ""

    if not title:
        return [
            _problem("عنوان SEO خالی است.")
        ]

    if not keyphrase:
        return []

    if _contains_keyphrase(title, keyphrase):
        return [
            _good(
                "عبارت کلیدی در عنوان SEO وجود دارد."
            )
        ]

    return [
        _improvement(
            "عبارت کلیدی در عنوان SEO وجود ندارد."
        )
    ]


def _check_keyphrase_in_description(
    seo, keyphrase
):
    description = (
        _get(seo, "description") or ""
    )

    if not description:
        return [
            _problem("توضیحات SEO خالی است.")
        ]

    if not keyphrase:
        return []

    if _contains_keyphrase(
        description, keyphrase
    ):
        return [
            _good(
                "عبارت کلیدی در توضیحات SEO وجود دارد."
            )
        ]

    return [
        _improvement(
            "عبارت کلیدی در توضیحات SEO وجود ندارد."
        )
    ]


def _check_keyphrase_in_url(seo, keyphrase):
    url = (
        _get(seo, "canonical", "url")
        or ""
    )

    if not url:
        return [
            _improvement(
                "Canonical / URL تعیین نشده است."
            )
        ]

    if not keyphrase:
        return []

    try:
        slug = (
            urlsplit(str(url))
            .path
            .rstrip("/")
            .split("/")[-1]
        )
    except ValueError:
        return [
            _improvement(
                "آدرس صفحه معتبر نیست."
            )
        ]

    slug = (
        slug.replace("-", " ")
        .replace("_", " ")
    )

    if _contains_keyphrase(
        slug, keyphrase
    ):
        return [
            _good(
                "عبارت کلیدی در URL وجود دارد."
            )
        ]

    return [
        _improvement(
            "عبارت کلیدی در URL وجود ندارد."
        )
    ]


# =====================================================
# Title and description length
# =====================================================

def _check_title_length(seo):
    title = _get(seo, "title") or ""

    if not title:
        return []

    length = len(str(title))

    if length < 30:
        return [
            _improvement(
                f"عنوان SEO کوتاه است ({length} کاراکتر). "
                "حداقل ۳۰ توصیه می‌شود."
            )
        ]

    if length > 60:
        return [
            _improvement(
                f"عنوان SEO بلند است ({length} کاراکتر). "
                "حداکثر ۶۰ توصیه می‌شود."
            )
        ]

    return [
        _good(
            f"طول عنوان SEO مناسب است ({length} کاراکتر)."
        )
    ]


def _check_description_length(seo):
    description = (
        _get(seo, "description") or ""
    )

    if not description:
        return []

    length = len(str(description))

    if length < 120:
        return [
            _improvement(
                f"توضیحات SEO کوتاه است ({length} کاراکتر). "
                "حداقل ۱۲۰ توصیه می‌شود."
            )
        ]

    if length > 160:
        return [
            _improvement(
                f"توضیحات SEO بلند است ({length} کاراکتر). "
                "حداکثر ۱۶۰ توصیه می‌شود."
            )
        ]

    return [
        _good(
            f"طول توضیحات SEO مناسب است ({length} کاراکتر)."
        )
    ]


# =====================================================
# Keyphrase density
# =====================================================

def _check_keyphrase_density(
    seo, keyphrase
):
    title = (
        _get(seo, "title") or ""
    )

    description = (
        _get(seo, "description") or ""
    )

    text = f"{title} {description}".strip()

    if not text or not keyphrase:
        return []

    density = _keyphrase_density(
        text, keyphrase
    )

    if density == 0:
        return [
            _improvement(
                "عبارت کلیدی در عنوان و توضیحات دیده نمی‌شود."
            )
        ]

    if density > 3.5:
        return [
            _problem(
                f"تراکم عبارت کلیدی زیاد است "
                f"({density:.2f}%). "
                "ممکن است اسپم تلقی شود."
            )
        ]

    if density < 0.5:
        return [
            _improvement(
                f"تراکم عبارت کلیدی کم است "
                f"({density:.2f}%)."
            )
        ]

    return [
        _good(
            f"تراکم عبارت کلیدی مناسب است "
            f"({density:.2f}%)."
        )
    ]


# =====================================================
# Canonical and robots
# =====================================================

def _check_canonical(seo):
    canonical = _get(
        seo, "canonical"
    )

    if not canonical:
        return [
            _improvement(
                "Canonical تعیین نشده است."
            )
        ]

    try:
        parts = urlsplit(
            str(canonical)
        )

        if (
            parts.scheme in ("http", "https")
            and parts.hostname
            and not parts.username
            and not parts.password
        ):
            return [
                _good(
                    "Canonical تعیین شده است."
                )
            ]

    except ValueError:
        pass

    return [
        _improvement(
            "آدرس Canonical معتبر نیست."
        )
    ]


def _check_robots(seo):
    index = (
        _get(seo, "index_control")
        or "index"
    )

    follow = (
        _get(seo, "follow_control")
        or "follow"
    )

    if (
        index == "index"
        and follow == "follow"
    ):
        return [
            _good(
                "Robots روی index,follow تنظیم شده است."
            )
        ]

    return [
        _improvement(
            f"Robots روی {index},{follow} تنظیم شده است."
        )
    ]


# =====================================================
# Schema
# =====================================================

def _check_schema(seo):
    schema_type = (
        _get(seo, "schema_type")
        or "auto"
    )

    schema_json = _get(
        seo, "schema_json"
    )

    if schema_json:
        return [
            _good(
                "Schema دستی تنظیم شده است."
            )
        ]

    if schema_type != "auto":
        return [
            _good(
                f"Schema نوع «{schema_type}» انتخاب شده است."
            )
        ]

    return [
        _improvement(
            "Schema خودکار است. "
            "برای دقت بیشتر، نوع Schema را تنظیم کنید."
        )
    ]


# =====================================================
# Open Graph and Twitter
# =====================================================

def _check_og(seo):
    results = []

    if _get(seo, "og_title"):
        results.append(
            _good(
                "عنوان Open Graph تنظیم شده است."
            )
        )
    else:
        results.append(
            _improvement(
                "عنوان Open Graph تنظیم نشده است."
            )
        )

    image = _get(
        seo,
        "og_image",
        "og_image_url",
    )

    if image:
        results.append(
            _good(
                "تصویر Open Graph تنظیم شده است."
            )
        )
    else:
        results.append(
            _improvement(
                "تصویر Open Graph تنظیم نشده است."
            )
        )

    return results


def _check_twitter(seo):
    if _get(seo, "twitter_card"):
        return [
            _good(
                "کارت توییتر تنظیم شده است."
            )
        ]

    return [
        _improvement(
            "کارت توییتر تنظیم نشده است."
        )
    ]


# =====================================================
# Content checks
# =====================================================

def _check_keyphrase_in_h1(
    seo, obj, keyphrase
):
    if obj is None or not keyphrase:
        return []

    title = _get(
        obj,
        "title_fa",
        "title_en",
        "title",
    )

    if not title:
        return []

    if _contains_keyphrase(
        title, keyphrase
    ):
        return [
            _good(
                "عبارت کلیدی در H1 "
                "(عنوان اصلی محتوا) وجود دارد."
            )
        ]

    return [
        _improvement(
            "عبارت کلیدی در H1 وجود ندارد."
        )
    ]


def _check_images_alt(seo, obj):
    if obj is None:
        return []

    images = []

    for field in (
        "image",
        "cover",
        "thumbnail",
    ):
        image = _get(obj, field)

        if image:
            images.append(
                (field, image)
            )

    if not images:
        return []

    missing = 0
    unknown = 0

    for field, image in images:
        alt = _get(
            image,
            "alt_text",
            "alt",
        )

        if not alt:
            alt = _get(
                obj,
                f"{field}_alt",
                f"{field}_alt_text",
                "image_alt",
                "alt_text",
            )

        if alt:
            continue

        # A Django ImageFieldFile does not contain
        # the final HTML alt attribute.
        if (
            hasattr(image, "url")
            and not hasattr(image, "alt")
            and not hasattr(
                image, "alt_text"
            )
        ):
            unknown += 1
        else:
            missing += 1

    if missing:
        return [
            _problem(
                f"{missing} تصویر بدون ALT ثبت‌شده وجود دارد."
            )
        ]

    if unknown:
        return [
            _improvement(
                "ALT تصاویر باید در قالب HTML صفحه "
                "بررسی شود؛ فیلد تصویر به‌تنهایی "
                "ALT را مشخص نمی‌کند."
            )
        ]

    return [
        _good(
            "همه تصاویر بررسی‌شده دارای ALT هستند."
        )
    ]


def _content(obj):
    return _get(
        obj,
        "description_fa",
        "description_en",
        "content_fa",
        "content_en",
        "body",
    ) or ""


def _internal_link(link):
    link = unescape(
        str(link)
    ).strip()

    if not link or link.startswith(
        ("//", "#")
    ):
        return False

    try:
        parts = urlsplit(link)
    except ValueError:
        return False

    if (
        not parts.scheme
        and not parts.netloc
    ):
        return bool(
            parts.path
            and not parts.path.startswith("//")
        )

    if (
        parts.scheme not in ("http", "https")
        or not parts.hostname
    ):
        return False

    hosts = {
        "nkavosh.com",
        "www.nkavosh.com",
    }

    configured = getattr(
        settings,
        "SITE_URL",
        "",
    )

    try:
        host = urlsplit(
            configured
        ).hostname

        if host:
            hosts.add(host.lower())

    except ValueError:
        pass

    return (
        parts.hostname.lower()
        in hosts
    )


def _check_internal_links(seo, obj):
    if obj is None:
        return []

    content = str(
        _content(obj)
    )

    if not _strip_html(
        content
    ).strip():
        return []

    links = re.findall(
        r'\bhref\s*=\s*["\']([^"\']+)["\']',
        content,
        flags=re.IGNORECASE,
    )

    internal = [
        link
        for link in links
        if _internal_link(link)
    ]

    if internal:
        return [
            _good(
                f"{len(internal)} لینک داخلی "
                "در محتوا وجود دارد."
            )
        ]

    return [
        _improvement(
            "هیچ لینک داخلی در محتوای "
            "بررسی‌شده دیده نمی‌شود."
        )
    ]


def _check_content_length(seo, obj):
    if obj is None:
        return []

    content = _content(obj)

    words = _word_count(
        _strip_html(content)
    )

    if words == 0:
        return [
            _improvement(
                "محتوای متنی برای تحلیل وجود ندارد."
            )
        ]

    if words < 300:
        return [
            _improvement(
                f"محتوای متنی کوتاه است ({words} کلمه). "
                "حداقل ۳۰۰ کلمه توصیه می‌شود."
            )
        ]

    if words > 2500:
        return [
            _improvement(
                f"محتوای متنی بلند است ({words} کلمه). "
                "ممکن است نیاز به تقسیم داشته باشد."
            )
        ]

    return [
        _good(
            f"طول محتوای متنی مناسب است "
            f"({words} کلمه)."
        )
    ]


# =====================================================
# Scoring
# =====================================================

WEIGHTS = {
    "good": 1.0,
    "improvement": 0.5,
    "problem": 0.0,
}


def _calculate_score(results):
    if not results:
        return 0

    total = sum(
        WEIGHTS.get(
            item.get("status"),
            0.0,
        )
        for item in results
    )

    return int(
        round(
            total / len(results) * 100
        )
    )


# =====================================================
# Public analysis entry point
# =====================================================

def analyze(seo, obj=None):
    if seo is None:
        item = _improvement(
            "SEO تنظیم نشده است."
        )

        return {
            "score": 0,
            "checks": {
                "good": [],
                "improvement": [item],
                "problem": [],
            },
            "flat": [item],
        }

    keyphrase = (
        _get(
            seo,
            "focus_keyphrase",
        )
        or ""
    )

    results = []

    results.extend(
        _check_keyphrase_presence(
            seo, keyphrase
        )
    )

    results.extend(
        _check_keyphrase_in_title(
            seo, keyphrase
        )
    )

    results.extend(
        _check_keyphrase_in_description(
            seo, keyphrase
        )
    )

    results.extend(
        _check_keyphrase_in_url(
            seo, keyphrase
        )
    )

    results.extend(
        _check_keyphrase_density(
            seo, keyphrase
        )
    )

    results.extend(
        _check_title_length(seo)
    )

    results.extend(
        _check_description_length(seo)
    )

    results.extend(
        _check_canonical(seo)
    )

    results.extend(
        _check_robots(seo)
    )

    results.extend(
        _check_schema(seo)
    )

    results.extend(
        _check_og(seo)
    )

    results.extend(
        _check_twitter(seo)
    )

    results.extend(
        _check_keyphrase_in_h1(
            seo, obj, keyphrase
        )
    )

    results.extend(
        _check_images_alt(
            seo, obj
        )
    )

    results.extend(
        _check_internal_links(
            seo, obj
        )
    )

    results.extend(
        _check_content_length(
            seo, obj
        )
    )

    checks = {
        status: [
            item
            for item in results
            if item["status"] == status
        ]
        for status in (
            "good",
            "improvement",
            "problem",
        )
    }

    return {
        "score": _calculate_score(
            results
        ),
        "checks": checks,
        "flat": results,
    }


# =====================================================
# Save SEO analysis
# =====================================================

def analyze_and_save(
    seo_setting, obj=None
):
    if seo_setting is None:
        return None

    from .models import SEOAnalysisLog

    result = analyze(
        seo_setting,
        obj=obj,
    )

    seo_setting.seo_score = (
        result["score"]
    )

    update_fields = [
        "seo_score"
    ]

    if any(
        field.name == "updated_at"
        for field in
        seo_setting._meta.concrete_fields
    ):
        update_fields.append(
            "updated_at"
        )

    seo_setting.save(
        update_fields=update_fields
    )

    SEOAnalysisLog.objects.create(
        seo_setting=seo_setting,
        score=result["score"],
        checks=result["checks"],
    )

    return result
