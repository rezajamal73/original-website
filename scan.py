# scan_seo_usage.py
"""
اسکنر وابستگی‌های SEOManager در کل پروژه.
بدون import کردن Django — فقط تحلیل متن.
"""

import ast
import os
from pathlib import Path
from collections import defaultdict

# ---- تنظیمات ----
ROOT = Path(__file__).resolve().parent

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "env", "__pycache__",
    "node_modules", "static", "media", "migrations",
    ".idea", ".vscode", "dist", "build",
}

# نام‌هایی که دنبالشونیم
TARGETS = {
    "SEOManager",
    "SEOManager.get_page",
    "SEOManager.get_object",
    "SEOManager.get_by_id",
    "SEOContext",
}

# ---- رنگ‌ها ----
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def find_python_files():
    for path in ROOT.rglob("*.py"):
        if should_skip(path):
            continue
        yield path


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def scan_file(path: Path):
    """برمی‌گردونه: لیست تاپل (line_no, code, kind)"""
    hits = []
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return hits

    lines = source.splitlines()

    # 1) اسکن متنی ساده (برای اطمینان)
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        for target in TARGETS:
            if target in stripped:
                hits.append((i, stripped, target))
                break

    return hits


def classify(kind: str) -> str:
    if kind == "SEOManager.get_page":
        return f"{GREEN}● get_page{RESET}"
    if kind == "SEOManager.get_object":
        return f"{GREEN}● get_object{RESET}"
    if kind == "SEOManager.get_by_id":
        return f"{GREEN}● get_by_id{RESET}"
    if kind == "SEOContext":
        return f"{YELLOW}○ SEOContext{RESET}"
    if kind == "SEOManager":
        return f"{CYAN}◇ SEOManager (عمومی){RESET}"
    return kind


def main():
    print(f"{BOLD}🔍 اسکن وابستگی‌های SEOManager در:{RESET} {ROOT}\n")

    total = 0
    by_kind = defaultdict(int)
    files_with_hits = defaultdict(list)

    for path in find_python_files():
        hits = scan_file(path)
        if not hits:
            continue
        files_with_hits[path] = hits
        for _, _, kind in hits:
            by_kind[kind] += 1
            total += 1

    if not files_with_hits:
        print(f"{RED}هیچ استفاده‌ای پیدا نشد.{RESET}")
        return

    # ---- گزارش فایل‌به‌فایل ----
    print(f"{BOLD}📁 گزارش فایل‌به‌فایل:{RESET}\n")

    for path in sorted(files_with_hits.keys(), key=lambda p: str(p)):
        print(f"{BOLD}{CYAN}{rel(path)}{RESET}")
        for line_no, code, kind in files_with_hits[path]:
            print(f"   خط {line_no:>4}  {classify(kind):<40}  {code[:100]}")
        print()

    # ---- خلاصه ----
    print(f"{BOLD}📊 خلاصه:{RESET}")
    print(f"   مجموع استفاده‌ها: {total}")
    print(f"   تعداد فایل‌ها:   {len(files_with_hits)}")
    print()
    print(f"{BOLD}بر اساس نوع:{RESET}")
    for kind, count in sorted(by_kind.items(), key=lambda x: -x[1]):
        print(f"   {classify(kind):<40}  {count}")

    print()
    print(f"{BOLD}✅ اگر همه‌ی get_page / get_object / get_by_id سالم بودن،")
    print(f"   بازنویسی داخلی app_seo/ هیچ ویویی رو نمی‌شکنه.{RESET}")


if __name__ == "__main__":
    main()