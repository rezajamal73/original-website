
import json

from django import template
from django.utils.safestring import mark_safe


register = template.Library()


@register.filter(name="safe_json_ld")
def safe_json_ld(value):
    """
    Safely render JSON-LD inside an HTML script tag.

    Accepts a JSON string, dict, or list.
    Invalid JSON is not rendered.
    """

    if value is None or value == "":
        return ""

    try:
        if isinstance(value, str):
            data = json.loads(value)

        elif isinstance(value, (dict, list)):
            data = value

        else:
            return ""

        if not isinstance(data, (dict, list)):
            return ""

        result = json.dumps(
            data,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )

        result = (
            result
            .replace("<", "\\u003C")
            .replace(">", "\\u003E")
            .replace("&", "\\u0026")
            .replace("\u2028", "\\u2028")
            .replace("\u2029", "\\u2029")
        )

        return mark_safe(result)

    except (TypeError, ValueError, OverflowError):
        return ""
