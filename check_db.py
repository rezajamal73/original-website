# check_db.py
import sqlite3
import os
from pathlib import Path

# مسیر دیتابیس — اگر اسم فایل چیز دیگری است، عوض کن
DB_PATH = Path("db.sqlite3")

if not DB_PATH.exists():
    print(f"❌ دیتابیس پیدا نشد: {DB_PATH.absolute()}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# جدول‌های موجود
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print("=" * 60)
print("جدول‌های موجود:")
print("=" * 60)
for t in sorted(tables):
    print(f"  - {t}")

# ستون‌های جدول companycatalog
print()
print("=" * 60)
print("ستون‌های app_catalog_companycatalog:")
print("=" * 60)

try:
    cursor.execute("PRAGMA table_info(app_catalog_companycatalog)")
    columns = cursor.fetchall()

    if not columns:
        print("❌ جدول app_catalog_companycatalog وجود ندارد")
    else:
        for col in columns:
            # col = (cid, name, type, notnull, dflt_value, pk)
            print(f"  - {col[1]:40s} {col[2]}")
except Exception as e:
    print(f"❌ خطا: {e}")

# چک migrationهای اعمال شده
print()
print("=" * 60)
print("migrationهای app_catalog:")
print("=" * 60)

try:
    cursor.execute("""
        SELECT name, applied
        FROM django_migrations
        WHERE app = 'app_catalog'
        ORDER BY name
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]:60s} {row[1]}")
except Exception as e:
    print(f"❌ خطا: {e}")

conn.close()