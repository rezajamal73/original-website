# app_seo/context_processors.py

def seo(request):
    """
    فقط request.seo را به context تزریق می‌کند.

    - اگر View خودش 'seo' را در context گذاشته باشد،
      به دلیل اولویت context view، این مقدار استفاده نمی‌شود.
    - اگر View چیزی نگذاشته باشد (مثلاً CBV یا صفحه‌ای که
      فراموش کرده)، این fallback عمل می‌کند.
    """

    return {
        "seo": getattr(request, "seo", None),
    }