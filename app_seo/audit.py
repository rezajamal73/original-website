
# app_seo/audit.py

"""
Audit logging for sensitive SEO administration actions.

This module uses Django's built-in LogEntry model.

No custom database table or migration is required.

Supported actions:
    - reanalyze
    - resync
    - rebuild

Supported outcomes:
    - success
    - failure
    - denied

The audit history can be viewed in the Django Admin
object history page.
"""

import json
import logging

from django.contrib.admin.models import (
    CHANGE,
    LogEntry,
)
from django.contrib.contenttypes.models import ContentType


logger = logging.getLogger(__name__)


ALLOWED_ACTIONS = {
    "reanalyze": "تحلیل مجدد SEO",
    "resync": "همگام‌سازی SEO",
    "rebuild": "بازسازی کامل SEO",
}

ALLOWED_OUTCOMES = {
    "success": "موفق",
    "failure": "ناموفق",
    "denied": "ردشده",
}


# ============================================================
# Safe text helpers
# ============================================================

def _safe_text(value, max_length=200):
    """
    Convert arbitrary values to bounded, printable text.

    Avoid including request bodies, passwords, tokens,
    or complete exception tracebacks in audit entries.
    """

    if value is None:
        return ""

    try:
        value = str(value)

    except Exception:
        return ""

    cleaned = "".join(
        character if character.isprintable() else " "
        for character in value
    )

    return cleaned.strip()[:max_length]


def _object_label(obj):
    """
    Build a readable object label without calling
    a potentially expensive custom __str__ method.
    """

    if obj is None:
        return "SEO"

    title = (
        getattr(obj, "title", None)
        or getattr(obj, "title_en", None)
        or getattr(obj, "page_key", None)
    )

    if title:
        return _safe_text(title, 180)

    object_id = getattr(obj, "pk", None)

    if object_id is not None:
        return f"SEO #{object_id}"

    return "SEO"


def _audit_message(action, outcome, details=""):
    """
    Create a structured Django Admin change message.

    Django Admin supports a JSON-encoded list of
    change descriptions in LogEntry.change_message.
    """

    action_label = ALLOWED_ACTIONS[action]
    outcome_label = ALLOWED_OUTCOMES[outcome]

    description = (
        f"{action_label} | نتیجه: {outcome_label}"
    )

    safe_details = _safe_text(
        details,
        max_length=300,
    )

    if safe_details:
        description += f" | {safe_details}"

    # Using Django Admin's expected structured format
    # allows the entry to appear correctly in history.
    return json.dumps(
        [
            {
                "changed": {
                    "fields": [
                        description,
                    ]
                }
            }
        ],
        ensure_ascii=False,
    )


# ============================================================
# Main audit function
# ============================================================

def record_seo_action(
    *,
    request,
    obj,
    action,
    outcome,
    details="",
):
    """
    Write a Django Admin LogEntry for an SEO action.

    Returns:
        True if the log entry was saved.
        False if the log entry could not be saved.

    Logging failures are reported to the server logger
    but are not raised to the caller.

    This is an operational audit trail. Database
    administrators can still modify these records.
    """

    if action not in ALLOWED_ACTIONS:
        logger.error(
            "SEO audit rejected unknown action: %s",
            _safe_text(action),
        )
        return False

    if outcome not in ALLOWED_OUTCOMES:
        logger.error(
            "SEO audit rejected unknown outcome: %s",
            _safe_text(outcome),
        )
        return False

    user = getattr(request, "user", None)

    if user is None:
        logger.warning(
            "SEO audit skipped: no request user"
        )
        return False

    if not getattr(
        user,
        "is_authenticated",
        False,
    ):
        logger.warning(
            "SEO audit skipped: unauthenticated user"
        )
        return False

    user_id = getattr(user, "pk", None)

    if user_id is None:
        logger.warning(
            "SEO audit skipped: user has no ID"
        )
        return False

    if obj is None:
        logger.warning(
            "SEO audit skipped: no SEO object"
        )
        return False

    object_id = getattr(obj, "pk", None)

    if object_id is None:
        logger.warning(
            "SEO audit skipped: unsaved SEO object"
        )
        return False

    try:
        content_type = ContentType.objects.get_for_model(
            obj,
            for_concrete_model=False,
        )

        message = _audit_message(
            action=action,
            outcome=outcome,
            details=details,
        )

        # Use the standard Django model manager rather
        # than version-dependent log_action methods.
        #
        # LogEntry.action_time is populated automatically
        # by Django when this record is created.
        LogEntry.objects.create(
            user_id=user_id,
            content_type_id=content_type.pk,
            object_id=str(object_id),
            object_repr=_object_label(obj),
            action_flag=CHANGE,
            change_message=message,
        )

        logger.info(
            "SEO audit saved: "
            "user_id=%s object_id=%s "
            "action=%s outcome=%s",
            user_id,
            object_id,
            action,
            outcome,
        )

        return True

    except Exception:
        logger.exception(
            "SEO audit save failed: "
            "user_id=%s object_id=%s "
            "action=%s outcome=%s",
            user_id,
            object_id,
            action,
            outcome,
        )

        return False


# ============================================================
# Convenience functions
# ============================================================

def record_seo_success(
    request,
    obj,
    action,
    details="",
):
    """
    Record a successful SEO operation.
    """

    return record_seo_action(
        request=request,
        obj=obj,
        action=action,
        outcome="success",
        details=details,
    )


def record_seo_failure(
    request,
    obj,
    action,
    details="",
):
    """
    Record a failed SEO operation.
    """

    return record_seo_action(
        request=request,
        obj=obj,
        action=action,
        outcome="failure",
        details=details,
    )


def record_seo_denied(
    request,
    obj,
    action,
    details="",
):
    """
    Record a denied SEO operation.
    """

    return record_seo_action(
        request=request,
        obj=obj,
        action=action,
        outcome="denied",
        details=details,
    )
