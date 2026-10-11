# show_structure.py
"""
نمایش ساختار کلی پروژه جنگو — بدون نیاز به دونستن اسم پروژه.
فقط توی ریشه پروژه (کنار manage.py) بذار و بزن:
    python show_structure.py
"""

import os
import re
import sys
from pathlib import Path


# =====================================================
# ۱. پیدا کردن manage.py و خواندن DJANGO_SETTINGS_MODULE
# =====================================================
def find_manage_py(start: Path) -> Path | None:
    """از پوشه فعلی به بالا دنبال manage.py می‌گرده."""
    current = start.resolve()
    for _ in range(5):  # حداکثر ۵ سطح بالاتر
        candidate = current / "manage.py"
        if candidate.exists():
            return candidate
        if current.parent == current:
            break
        current = current.parent
    return None


def read_settings_module(manage_py: Path) -> str | None:
    """از داخل manage.py مقدار DJANGO_SETTINGS_MODULE رو استخراج می‌کنه."""
    try:
        content = manage_py.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    match = re.search(
        r'DJANGO_SETTINGS_MODULE["\']?\s*,\s*["\']([\w\.]+)["\']',
        content,
    )
    if match:
        return match.group(1)
    return None


# اگه از قبل ست نشده، خودمون ست کنیم
if not os.environ.get("DJANGO_SETTINGS_MODULE"):
    manage_py = find_manage_py(Path.cwd())

    if not manage_py:
        print("❌ فایل manage.py پیدا نشد.")
        print("💡 این اسکریپت رو توی ریشه پروژه (کنار manage.py) بذار.")
        sys.exit(1)

    # مسیر ریشه پروژه رو به sys.path اضافه کن
    project_root = manage_py.parent
    sys.path.insert(0, str(project_root))

    settings_module = read_settings_module(manage_py)
    if not settings_module:
        print("❌ نتونستم DJANGO_SETTINGS_MODULE رو از manage.py بخونم.")
        sys.exit(1)

    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
    print(f"✅ DJANGO_SETTINGS_MODULE = {settings_module}")


# =====================================================
# ۲. راه‌اندازی جنگو
# =====================================================
import django

try:
    django.setup()
except Exception as e:
    print(f"❌ خطا در راه‌اندازی جنگو: {e}")
    sys.exit(1)

from django.apps import apps
from django.conf import settings
from django.db import connection
from django.db.models import FileField, ImageField


# =====================================================
# رنگ‌ها
# =====================================================
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"


def header(title):
    print(f"\n{C.BOLD}{C.CYAN}{'═' * 70}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}  {title}{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}{'═' * 70}{C.RESET}")


def subheader(title):
    print(f"\n{C.BOLD}{C.MAGENTA}▸ {title}{C.RESET}")
    print(f"{C.DIM}{'─' * 60}{C.RESET}")


def info(label, value, color=C.GREEN):
    print(f"  {C.DIM}{label}:{C.RESET} {color}{value}{C.RESET}")


# =====================================================
# ۳. اطلاعات کلی
# =====================================================
header("📦 اطلاعات کلی پروژه")
info("Django version", django.get_version())
info("BASE_DIR", str(settings.BASE_DIR))
info("DEBUG", str(settings.DEBUG), C.YELLOW if settings.DEBUG else C.GREEN)
info("MEDIA_ROOT", str(settings.MEDIA_ROOT))
info("MEDIA_URL", str(settings.MEDIA_URL))
info("STATIC_URL", str(getattr(settings, "STATIC_URL", "—")))
info("DATABASE", settings.DATABASES["default"]["ENGINE"])


# =====================================================
# ۴. اپ‌ها
# =====================================================
header("🧩 اپ‌ها")

local_apps = []
third_party_apps = []

base_dir_str = str(settings.BASE_DIR)
for app_config in apps.get_app_configs():
    if str(app_config.path).startswith(base_dir_str):
        local_apps.append(app_config)
    else:
        third_party_apps.append(app_config)

subheader(f"اپ‌های پروژه ({len(local_apps)})")
for app in sorted(local_apps, key=lambda a: a.label):
    n_models = len(list(app.get_models()))
    print(
        f"  {C.GREEN}✓{C.RESET} {C.BOLD}{app.label:<25}{C.RESET} "
        f"{C.DIM}{n_models} مدل{C.RESET}  {C.DIM}{app.verbose_name}{C.RESET}"
    )

subheader(f"اپ‌های خارجی ({len(third_party_apps)})")
for app in sorted(third_party_apps, key=lambda a: a.label):
    print(f"  {C.DIM}• {app.label}{C.RESET}")


# =====================================================
# ۵. مدل‌ها و فیلدهای فایل‌دار
# =====================================================
header("📁 مدل‌ها و فیلدهای فایل‌دار")

total_models = 0
total_file_fields = 0

for app in sorted(local_apps, key=lambda a: a.label):
    models_with_files = []

    for model in app.get_models():
        total_models += 1
        file_fields = []

        for field in model._meta.get_fields():
            if isinstance(field, (FileField, ImageField)):
                upload_to = getattr(field, "upload_to", "—")

                # اگه partial هست، subfolder رو دربیار
                if hasattr(upload_to, "keywords"):
                    sub = upload_to.keywords.get("subfolder", "?")
                    display = f"<app_label>/{sub}/"
                elif hasattr(upload_to, "func") and hasattr(upload_to, "keywords"):
                    display = str(upload_to)
                else:
                    display = str(upload_to)

                file_fields.append({
                    "name": field.name,
                    "type": "Image" if isinstance(field, ImageField) else "File",
                    "upload_to": display,
                })
                total_file_fields += 1

        if file_fields:
            models_with_files.append((model, file_fields))

    if models_with_files:
        subheader(f"📦 {app.label}")
        for model, fields in models_with_files:
            print(f"  {C.BOLD}{C.YELLOW}{model.__name__}{C.RESET}")
            for f in fields:
                icon = "🖼️ " if f["type"] == "Image" else "📄"
                print(
                    f"    {icon} {C.CYAN}{f['name']:<22}{C.RESET} "
                    f"→ {C.GREEN}media/{f['upload_to']}...{C.RESET}"
                )

info("\nجمع کل مدل‌ها", total_models, C.CYAN)
info("جمع کل فیلدهای فایل‌دار", total_file_fields, C.CYAN)


# =====================================================
# ۶. ساختار پوشه media
# =====================================================
header("🗂️  ساختار پوشه media")

media_root = Path(settings.MEDIA_ROOT)

if not media_root.exists():
    print(f"  {C.YELLOW}⚠ پوشه media وجود نداره: {media_root}{C.RESET}")
else:
    def walk_dir(path: Path, prefix="", max_depth=3, depth=0):
        if depth >= max_depth:
            return
        try:
            items = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
        except PermissionError:
            return

        dirs = [i for i in items if i.is_dir()]
        files = [i for i in items if i.is_file()]

        for d in dirs:
            try:
                count = sum(1 for _ in d.rglob("*") if _.is_file())
            except Exception:
                count = "?"
            print(f"  {prefix}📁 {C.BOLD}{d.name}{C.RESET}/ {C.DIM}({count} فایل){C.RESET}")
            walk_dir(d, prefix + "   ", max_depth, depth + 1)

        for f in files[:3]:
            try:
                size_kb = f.stat().st_size / 1024
                print(f"  {prefix}📄 {C.DIM}{f.name} ({size_kb:.1f} KB){C.RESET}")
            except Exception:
                pass
        if len(files) > 3:
            print(f"  {prefix}{C.DIM}... و {len(files) - 3} فایل دیگه{C.RESET}")

    walk_dir(media_root)


# =====================================================
# ۷. وضعیت migrations
# =====================================================
header("🔄 وضعیت migrations")

from django.db.migrations.executor import MigrationExecutor

executor = MigrationExecutor(connection)
plan = executor.migration_plan(executor.loader.graph.leaf_nodes())

if not plan:
    print(f"  {C.GREEN}✓ همه migrations اعمال شده‌اند{C.RESET}")
else:
    print(f"  {C.YELLOW}⚠ {len(plan)} migration اعمال‌نشده:{C.RESET}")
    for migration, backwards in plan:
        direction = "↓ برگشت" if backwards else "↑ اعمال"
        print(f"    {C.YELLOW}{direction}{C.RESET} {migration.app_label}.{migration.name}")


# =====================================================
# ۸. جدول‌های دیتابیس
# =====================================================
header("🗄️  جدول‌های دیتابیس")

try:
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names(cursor)
    info("تعداد جدول‌ها", len(tables), C.CYAN)
    for t in sorted(tables)[:30]:
        print(f"  {C.DIM}• {t}{C.RESET}")
    if len(tables) > 30:
        print(f"  {C.DIM}... و {len(tables) - 30} جدول دیگه{C.RESET}")
except Exception as e:
    print(f"  {C.RED}❌ خطا در اتصال به دیتابیس: {e}{C.RESET}")


# =====================================================
# پایان
# =====================================================
print(f"\n{C.BOLD}{C.GREEN}{'═' * 70}{C.RESET}")
print(f"{C.BOLD}{C.GREEN}  ✅ گزارش کامل شد{C.RESET}")
print(f"{C.BOLD}{C.GREEN}{'═' * 70}{C.RESET}\n")