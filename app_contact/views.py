# app_contact/views.py

import random

from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib import messages

from .models import ContactMessage


# =====================================================
# CAPTCHA GENERATOR
# =====================================================
def _generate_captcha():
    return "".join(
        random.choice("0123456789")
        for _ in range(5)
    )


# =====================================================
# CONTACT SUBMIT
# =====================================================
@require_POST
def contact_submit(request):

    user_captcha = request.POST.get(
        "captcha",
        ""
    ).strip()

    real_captcha = request.session.get(
        "contact_captcha"
    )


    # بررسی کپچا
    if not real_captcha or user_captcha != real_captcha:

        messages.error(
            request,
            "کد امنیتی اشتباه است."
        )

        return redirect(
            request.META.get(
                "HTTP_REFERER",
                "/"
            )
        )


    # ذخیره پیام تماس
    ContactMessage.objects.create(

        first_name=request.POST.get(
            "first_name",
            ""
        ),

        last_name=request.POST.get(
            "last_name",
            ""
        ),

        phone=request.POST.get(
            "phone",
            ""
        ),

        email=request.POST.get(
            "email",
            ""
        ),

        subject=request.POST.get(
            "subject",
            ""
        ),

        message=request.POST.get(
            "message",
            ""
        ),
    )


    messages.success(
        request,
        "پیام شما با موفقیت ارسال شد."
    )


    # ساخت کپچای جدید بعد از ارسال موفق
    request.session["contact_captcha"] = _generate_captcha()
    request.session.modified = True


    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "/"
        )
    )