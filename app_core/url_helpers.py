"""
توابع کمکی برای تشخیص زبان درخواست.
"""


def is_english_request(request):
    """
    تشخیص درخواست انگلیسی.
    """
    match = request.resolver_match

    if match:
        if match.namespace and match.namespace.endswith("_en"):
            return True
        if match.url_name and match.url_name.endswith("_en"):
            return True

    if request.path.startswith("/en/"):
        return True

    return False