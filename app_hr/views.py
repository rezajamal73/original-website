import random

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages

from app_hr.models import JobOpportunity, JobApplication
from app_seo.utils import SEOManager


def _generate_captcha():
    return "".join(random.choice("0123456789") for _ in range(5))


# =====================================================
# HR HOME
# =====================================================
def hr_home(request):
    queryset = (
        JobOpportunity.objects
        .filter(is_active=True)
        .order_by("-created_at_fa", "ordering")
    )

    paginator = Paginator(queryset, 8)
    page_number = request.GET.get("page")

    try:
        job_list = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        job_list = paginator.get_page(1)

    context = {
        "job_list": job_list,
        "seo": SEOManager.get_page("hr"),
    }

    return render(
        request,
        "RTL/hr/hr_home.html",
        context
    )


# =====================================================
# HR SINGLE + CAPTCHA
# =====================================================
def hr_single(request, pid):
    job = get_object_or_404(
        JobOpportunity.objects.filter(is_active=True),
        pk=pid
    )

    # 🔐 ساخت کپچا برای نمایش
    if "hr_captcha" not in request.session:
        request.session["hr_captcha"] = _generate_captcha()
        request.session.modified = True


    if request.method == "POST" and job.recruitment_status == "open":

        user_captcha = request.POST.get("captcha", "").strip()
        real_captcha = request.session.get("hr_captcha")


        # ❌ بررسی کپچا
        if not real_captcha or user_captcha != real_captcha:
            messages.error(request, "کد امنیتی اشتباه است.")
            return redirect(request.path)


        # ✅ ذخیره درخواست شغلی
        JobApplication.objects.create(
            opportunity=job,
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            national_code=request.POST.get("national_code"),
            gender=request.POST.get("gender"),
            age=request.POST.get("age"),
            marital_status=request.POST.get("marital_status"),
            military_status=request.POST.get("military_status"),
            mobile=request.POST.get("mobile"),
            email=request.POST.get("email"),
            resume_file=request.FILES.get("resume_file"),
            ip_address=request.META.get("REMOTE_ADDR"),
        )


        messages.success(
            request,
            "✅ درخواست شما با موفقیت ثبت شد و پس از بررسی با شما تماس گرفته خواهد شد."
        )


        # 🔄 تولید کپچای جدید بعد از ارسال
        request.session["hr_captcha"] = _generate_captcha()
        request.session.modified = True

        return redirect(request.path)


    context = {
        "job": job,
        "captcha_code": request.session.get("hr_captcha"),
        "seo": SEOManager.get_object(job),
    }


    return render(
        request,
        "RTL/hr/hr_single.html",
        context
    )