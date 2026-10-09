"""
fix_all_ltr_links_v3.py
اصلاح نهایی و جامع لینک‌های namespace در قالب‌های LTR

این نسخه، همه اپ‌هایی که قالب LTR دارن رو دوزبانه فرض می‌کنه.

نحوه استفاده:
1. برای همه اپ‌ها urls_en.py بساز (اگه نداری)
2. توی original_website/urls.py همه رو فعال کن
3. این اسکریپت رو اجرا کن
"""

import re
from pathlib import Path


TEMPLATES_DIR = Path("templates/LTR")


# =====================================================
# اپ‌هایی که دوزبانه هستن (urls_en.py دارن)
# =====================================================
# ✅ همه اپ‌هایی که قالب LTR دارن
BILINGUAL_APPS = {
    "app_core",
    "app_product",
    "app_blog",
    "app_catalog",
    "app_chart",
    "app_media",
    "app_resume",
    "app_reports",
    "app_security",
    "app_contact",
}


# =====================================================
# لیست همه اپ‌ها (برای تشخیص namespace درست)
# =====================================================
ALL_APPS = {
    "app_admin",
    "app_core",
    "app_product",
    "app_chart",
    "app_blog",
    "app_media",
    "app_catalog",
    "app_reports",
    "app_resume",
    "app_hr",
    "app_news",
    "app_security",
    "app_contact",
    "app_seo",
    "app_auction",
    "app_tender",
    "app_inquiry",
    "app_sale",
    "app_log",
    "app_visit",
    "app_backup",
    "app_banner",
}


# =====================================================
# تابع تعیین namespace درست
# =====================================================
def get_correct_namespace(app_name: str, url_name: str) -> str:
    """
    تعیین namespace درست بر اساس اپ و url_name
    """
    is_bilingual = app_name in BILINGUAL_APPS
    has_en_suffix = url_name.endswith("_en")

    if is_bilingual and has_en_suffix:
        # اپ دوزبانه + url_name انگلیسی → namespace انگلیسی
        return f"{app_name}_en:{url_name}"

    if is_bilingual and not has_en_suffix:
        # اپ دوزبانه + url_name فارسی → namespace فارسی
        return f"{app_name}:{url_name}"

    if not is_bilingual and has_en_suffix:
        # اپ غیر دوزبانه + url_name انگلیسی → به فارسی برگردون
        base_url_name = url_name[:-3]  # حذف _en
        return f"{app_name}:{base_url_name}"

    # اپ غیر دوزبانه + url_name فارسی
    return f"{app_name}:{url_name}"


# =====================================================
# الگوی پیدا کردن namespace در url tags
# =====================================================
URL_PATTERN = re.compile(
    r"""\{%\s*url\s+['"]([a-z_]+):([a-z_0-9]+)['"]"""
)


def fix_content(content: str) -> tuple[str, int]:
    """
    اصلاح محتوای یه فایل
    خروجی: (محتوای جدید, تعداد تغییرات)
    """
    changes = 0
    result_parts = []
    last_end = 0

    for match in URL_PATTERN.finditer(content):
        app_name = match.group(1)
        url_name = match.group(2)

        # بررسی که app_name توی لیست اپ‌های ما هست یا نه
        base_app = app_name
        if app_name.endswith("_en"):
            base_app = app_name[:-3]

        if base_app not in ALL_APPS:
            # اپ ناشناخته — دست نزن
            continue

        correct_namespace = get_correct_namespace(base_app, url_name)

        # اگه namespace فعلی درست نبود، اصلاح کن
        current_namespace = f"{app_name}:{url_name}"
        if current_namespace != correct_namespace:
            # جایگزینی
            result_parts.append(content[last_end:match.start()])
            result_parts.append(f"{{% url '{correct_namespace}'")
            last_end = match.end()
            changes += 1

    if changes == 0:
        return content, 0

    # اضافه کردن باقی محتوا
    result_parts.append(content[last_end:])
    new_content = "".join(result_parts)

    return new_content, changes


def fix_file(filepath: Path) -> int:
    """اصلاح یه فایل. تعداد تغییرات رو برمی‌گردونه."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return 0

    new_content, changes = fix_content(content)

    if changes > 0:
        filepath.write_text(new_content, encoding="utf-8")

    return changes


def find_remaining_issues():
    """پیدا کردن لینک‌های اشتباه باقی‌مونده"""
    print()
    print("=" * 60)
    print("🔍 بررسی نهایی")
    print("=" * 60)

    issues = []

    for html_file in sorted(TEMPLATES_DIR.rglob("*.html")):
        try:
            content = html_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for match in URL_PATTERN.finditer(content):
            app_name = match.group(1)
            url_name = match.group(2)

            base_app = app_name[:-3] if app_name.endswith("_en") else app_name

            if base_app not in ALL_APPS:
                continue

            correct_namespace = get_correct_namespace(base_app, url_name)
            current_namespace = f"{app_name}:{url_name}"

            if current_namespace != correct_namespace:
                line_no = content[:match.start()].count("\n") + 1
                issues.append((html_file, line_no, current_namespace, correct_namespace))

    if not issues:
        print("  ✅ همه لینک‌ها درست هستن!")
    else:
        print(f"  ⚠️  {len(issues)} لینک اشتباه باقی‌مونده:")
        for filepath, line_no, current, correct in issues[:30]:
            relative = filepath.relative_to(TEMPLATES_DIR.parent.parent)
            print(f"     {relative}:{line_no}")
            print(f"       → {current}")
            print(f"       ← باید بشه: {correct}")

        if len(issues) > 30:
            print(f"     ... و {len(issues) - 30} مورد دیگه")

    return len(issues)


def main():
    print("=" * 60)
    print("🔧 اصلاح جامع لینک‌های namespace در قالب‌های LTR")
    print("=" * 60)
    print()
    print(f"📁 پوشه: {TEMPLATES_DIR.resolve()}")
    print(f"🌐 اپ‌های دوزبانه: {', '.join(sorted(BILINGUAL_APPS))}")
    print()

    total_files = 0
    total_changes = 0

    for html_file in sorted(TEMPLATES_DIR.rglob("*.html")):
        changes = fix_file(html_file)
        if changes > 0:
            total_files += 1
            total_changes += changes
            relative = html_file.relative_to(TEMPLATES_DIR.parent.parent)
            print(f"  ✅ {relative}  ({changes} تغییر)")

    print()
    print("=" * 60)
    print(f"📊 فایل‌های اصلاح‌شده: {total_files}")
    print(f"📊 کل تغییرات: {total_changes}")
    print("=" * 60)

    # بررسی نهایی
    remaining = find_remaining_issues()

    print()
    print("=" * 60)
    if remaining == 0:
        print("🎉 همه چیز درست هست!")
    else:
        print(f"⚠️  {remaining} مورد نیاز به بررسی دستی داره")
        print()
        print("راه‌حل:")
        print("1. برای اپ‌های باقی‌مونده urls_en.py بساز")
        print("2. توی original_website/urls.py فعالشون کن")
        print("3. دوباره این اسکریپت رو اجرا کن")
    print("=" * 60)


if __name__ == "__main__":
    main()