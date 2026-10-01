# app_seo/analyzer.py

import re

from django.conf import settings


# =====================================================
#  کمک‌تابع‌ها
# =====================================================

def _get(obj, *names, default=None):
    for name in names:
        value = getattr(obj, name, None)
        if value is not None and value != "":
            return value
    return default


def _normalize(text):
    if not text:
        return ""
    text = str(text).lower()
    text = text.replace("\u200c", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _word_count(text):
    if not text:
        return 0
    return len(_normalize(text).split())


def _contains_keyphrase(text, keyphrase):
    if not text or not keyphrase:
        return False
    return _normalize(keyphrase) in _normalize(text)


def _count_keyphrase(text, keyphrase):
    if not text or not keyphrase:
        return 0
    return _normalize(text).count(_normalize(keyphrase))


def _keyphrase_density(text, keyphrase):
    if not text or not keyphrase:
        return 0.0
    words = _word_count(text)
    if words == 0:
        return 0.0
    occurrences = _count_keyphrase(text, keyphrase)
    keyphrase_words = _word_count(keyphrase)
    return (occurrences * keyphrase_words) / words * 100


def _strip_html(text):
    if not text:
        return ""
    return re.sub(r"<[^>]+>", " ", str(text))


# =====================================================
#  ساختار نتایج
# =====================================================

def _good(message):
    return {"status": "good", "message": message, "icon": "🟢"}


def _improvement(message):
    return {"status": "improvement", "message": message, "icon": "🟡"}


def _problem(message):
    return {"status": "problem", "message": message, "icon": "🔴"}


# =====================================================
#  چک‌های SEO  —  پایه
# =====================================================

def _check_keyphrase_presence(seo, keyphrase):
    if not keyphrase:
        return [_problem("عبارت کلیدی اصلی تعیین نشده است.")]
    return []


def _check_keyphrase_in_title(seo, keyphrase):
    title = _get(seo, "title") or ""
    if not title:
        return [_problem("عنوان SEO خالی است.")]

    if not keyphrase:
        return []

    if _contains_keyphrase(title, keyphrase):
        return [_good("عبارت کلیدی در عنوان SEO وجود دارد.")]

    return [_improvement("عبارت کلیدی در عنوان SEO وجود ندارد.")]


def _check_keyphrase_in_description(seo, keyphrase):
    description = _get(seo, "description") or ""
    if not description:
        return [_problem("توضیحات SEO خالی است.")]

    if not keyphrase:
        return []

    if _contains_keyphrase(description, keyphrase):
        return [_good("عبارت کلیدی در توضیحات SEO وجود دارد.")]

    return [_improvement("عبارت کلیدی در توضیحات SEO وجود ندارد.")]


def _check_keyphrase_in_url(seo, keyphrase):
    url = _get(seo, "canonical", "url") or ""
    if not url:
        return [_improvement("Canonical / URL تعیین نشده است.")]

    if not keyphrase:
        return []

    slug = url.rstrip("/").split("/")[-1]
    slug = slug.replace("-", " ").replace("_", " ")

    if _contains_keyphrase(slug, keyphrase):
        return [_good("عبارت کلیدی در URL وجود دارد.")]

    return [_improvement("عبارت کلیدی در URL وجود ندارد.")]


def _check_title_length(seo):
    title = _get(seo, "title") or ""
    if not title:
        return []

    length = len(title)

    if length < 30:
        return [_improvement(f"عنوان SEO کوتاه است ({length} کاراکتر). حداقل ۳۰ توصیه می‌شود.")]

    if length > 60:
        return [_improvement(f"عنوان SEO بلند است ({length} کاراکتر). حداکثر ۶۰ توصیه می‌شود.")]

    return [_good(f"طول عنوان SEO مناسب است ({length} کاراکتر).")]


def _check_description_length(seo):
    description = _get(seo, "description") or ""
    if not description:
        return []

    length = len(description)

    if length < 120:
        return [_improvement(f"توضیحات SEO کوتاه است ({length} کاراکتر). حداقل ۱۲۰ توصیه می‌شود.")]

    if length > 160:
        return [_improvement(f"توضیحات SEO بلند است ({length} کاراکتر). حداکثر ۱۶۰ توصیه می‌شود.")]

    return [_good(f"طول توضیحات SEO مناسب است ({length} کاراکتر).")]


def _check_keyphrase_density(seo, keyphrase):
    description = _get(seo, "description") or ""
    title = _get(seo, "title") or ""

    text = f"{title} {description}"

    if not text or not keyphrase:
        return []

    density = _keyphrase_density(text, keyphrase)

    if density == 0:
        return [_improvement("عبارت کلیدی در متن اصلی دیده نمی‌شود.")]

    if density > 3.5:
        return [_problem(f"تراکم عبارت کلیدی زیاد است ({density:.2f}%). ممکن است اسپم تلقی شود.")]

    if density < 0.5:
        return [_improvement(f"تراکم عبارت کلیدی کم است ({density:.2f}%).")]

    return [_good(f"تراکم عبارت کلیدی مناسب است ({density:.2f}%).")]


def _check_canonical(seo):
    canonical = _get(seo, "canonical")
    if canonical:
        return [_good("Canonical تعیین شده است.")]
    return [_improvement("Canonical تعیین نشده است.")]


def _check_robots(seo):
    # روی SEOContext، این‌ها property هستند و از robots محاسبه می‌شوند
    index = _get(seo, "index_control") or "index"
    follow = _get(seo, "follow_control") or "follow"

    if index == "index" and follow == "follow":
        return [_good("Robots روی index,follow تنظیم شده است.")]

    return [_improvement(f"Robots روی {index},{follow} تنظیم شده است.")]


def _check_schema(seo):
    schema_type = _get(seo, "schema_type") or "auto"
    schema_json = _get(seo, "schema_json")

    if schema_json:
        return [_good("Schema دستی تنظیم شده است.")]

    if schema_type and schema_type != "auto":
        return [_good(f"Schema نوع «{schema_type}» انتخاب شده است.")]

    return [_improvement("Schema خودکار است. برای دقت بیشتر، نوع Schema را تنظیم کنید.")]


def _check_og(seo):
    results = []

    if _get(seo, "og_title"):
        results.append(_good("عنوان Open Graph تنظیم شده است."))
    else:
        results.append(_improvement("عنوان Open Graph تنظیم نشده است."))

    # og_image ممکن است ImageFieldFile باشد
    og_image = getattr(seo, "og_image", None) if seo else None
    if og_image:
        results.append(_good("تصویر Open Graph تنظیم شده است."))
    else:
        results.append(_improvement("تصویر Open Graph تنظیم نشده است."))

    return results


def _check_twitter(seo):
    if _get(seo, "twitter_card"):
        return [_good("کارت توییتر تنظیم شده است.")]
    return [_improvement("کارت توییتر تنظیم نشده است.")]


# =====================================================
#  چک‌های محتوایی
# =====================================================

def _check_keyphrase_in_h1(seo, obj, keyphrase):
    if obj is None or not keyphrase:
        return []

    title = (
        getattr(obj, "title_fa", None)
        or getattr(obj, "title_en", None)
        or getattr(obj, "title", None)
    )

    if not title:
        return []

    if _contains_keyphrase(title, keyphrase):
        return [_good("عبارت کلیدی در H1 (عنوان اصلی محتوا) وجود دارد.")]

    return [_improvement("عبارت کلیدی در H1 وجود ندارد.")]


def _check_images_alt(seo, obj):
    if obj is None:
        return []

    images = []
    for field in ("image", "cover", "thumbnail"):
        img = getattr(obj, field, None)
        if img:
            images.append(img)

    if not images:
        return []

    missing_alt = 0
    for img in images:
        alt = getattr(img, "alt_text", None) or getattr(img, "alt", None)
        if not alt:
            missing_alt += 1

    if missing_alt == 0:
        return [_good("همه تصاویر دارای ALT هستند.")]

    return [_problem(f"{missing_alt} تصویر بدون ALT وجود دارد.")]


def _check_internal_links(seo, obj):
    if obj is None:
        return []

    content = (
        getattr(obj, "description_fa", None)
        or getattr(obj, "description_en", None)
        or getattr(obj, "content_fa", None)
        or getattr(obj, "content_en", None)
        or getattr(obj, "body", None)
        or ""
    )

    text = _strip_html(content)
    links = re.findall(r'href=["\']([^"\']+)["\']', str(content))

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")

    internal = []
    for link in links:
        if link.startswith("/"):
            internal.append(link)
        elif site_url and link.startswith(site_url):
            internal.append(link)

    if not text:
        return []

    if internal:
        return [_good(f"{len(internal)} لینک داخلی در محتوا وجود دارد.")]

    return [_improvement("هیچ لینک داخلی در محتوا دیده نمی‌شود.")]


def _check_content_length(seo, obj):
    if obj is None:
        return []

    content = (
        getattr(obj, "description_fa", None)
        or getattr(obj, "description_en", None)
        or getattr(obj, "content_fa", None)
        or getattr(obj, "content_en", None)
        or getattr(obj, "body", None)
        or ""
    )

    text = _strip_html(content)
    words = _word_count(text)

    if words == 0:
        return [_improvement("محتوای متنی برای تحلیل وجود ندارد.")]

    if words < 300:
        return [_improvement(f"محتوای متنی کوتاه است ({words} کلمه). حداقل ۳۰۰ کلمه توصیه می‌شود.")]

    if words > 2500:
        return [_improvement(f"محتوای متنی بلند است ({words} کلمه). ممکن است نیاز به تقسیم داشته باشد.")]

    return [_good(f"طول محتوای متنی مناسب است ({words} کلمه).")]


# =====================================================
#  وزن‌دهی امتیاز
# =====================================================

WEIGHTS = {
    "good": 1.0,
    "improvement": 0.5,
    "problem": 0.0,
}


def _calculate_score(results):
    if not results:
        return 0

    total = 0.0
    for item in results:
        total += WEIGHTS.get(item["status"], 0.0)

    return int(round(total / len(results) * 100))


# =====================================================
#  Analyzer  —  نقطه ورود عمومی
# =====================================================

def analyze(seo, obj=None):
    if seo is None:
        return {
            "score": 0,
            "checks": {
                "good": [],
                "improvement": [_improvement("SEO تنظیم نشده است.")],
                "problem": [],
            },
            "flat": [],
        }

    keyphrase = _get(seo, "focus_keyphrase") or ""

    results = []

    # ---------- Yoast-style checks ----------

    results.extend(_check_keyphrase_presence(seo, keyphrase))
    results.extend(_check_keyphrase_in_title(seo, keyphrase))
    results.extend(_check_keyphrase_in_description(seo, keyphrase))
    results.extend(_check_keyphrase_in_url(seo, keyphrase))
    results.extend(_check_keyphrase_density(seo, keyphrase))

    results.extend(_check_title_length(seo))
    results.extend(_check_description_length(seo))

    results.extend(_check_canonical(seo))
    results.extend(_check_robots(seo))
    results.extend(_check_schema(seo))
    results.extend(_check_og(seo))
    results.extend(_check_twitter(seo))

    # ---------- محتوا ----------

    results.extend(_check_keyphrase_in_h1(seo, obj, keyphrase))
    results.extend(_check_images_alt(seo, obj))
    results.extend(_check_internal_links(seo, obj))
    results.extend(_check_content_length(seo, obj))

    # ---------- دسته‌بندی ----------

    good = [r for r in results if r["status"] == "good"]
    improvement = [r for r in results if r["status"] == "improvement"]
    problem = [r for r in results if r["status"] == "problem"]

    score = _calculate_score(results)

    return {
        "score": score,
        "checks": {
            "good": good,
            "improvement": improvement,
            "problem": problem,
        },
        "flat": results,
    }


# =====================================================
#  ذخیره تحلیل روی SEOSetting
# =====================================================

def analyze_and_save(seo_setting, obj=None):
    if seo_setting is None:
        return None

    from .models import SEOAnalysisLog

    result = analyze(seo_setting, obj=obj)

    seo_setting.seo_score = result["score"]
    seo_setting.save(update_fields=["seo_score", "updated_at"])

    SEOAnalysisLog.objects.create(
        seo_setting=seo_setting,
        score=result["score"],
        checks={
            "good": result["checks"]["good"],
            "improvement": result["checks"]["improvement"],
            "problem": result["checks"]["problem"],
        },
    )

    return result