# app_tender/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q

from app_tender.models import Tender, TenderTag
from app_seo.utils import SEOManager

# ✅ is_english_request از app_core
from app_core.url_helpers import is_english_request


# =====================================================
# PAGINATION HELPER
# =====================================================
def paginate_queryset(request, queryset, per_page=8):
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get("page")

    try:
        return paginator.get_page(page_number)
    except PageNotAnInteger:
        return paginator.get_page(1)
    except EmptyPage:
        return paginator.get_page(paginator.num_pages)


# =====================================================
# TENDER HOME
# =====================================================
def tender_home(request, cat_name=None, author_username=None):
    is_english = is_english_request(request)

    tenders_qs = Tender.objects.all().order_by("-created_at_fa")

    if cat_name:
        if is_english:
            tenders_qs = tenders_qs.filter(category__title_en=cat_name)
        else:
            tenders_qs = tenders_qs.filter(category__title_fa=cat_name)

    if author_username:
        tenders_qs = tenders_qs.filter(author__username=author_username)

    tenders = paginate_queryset(request, tenders_qs)

    template_name = (
        "LTR/tender/tender-home.html"
        if is_english
        else "RTL/tender/tender-home.html"
    )

    context = {
        "tenders": tenders,
        "seo": SEOManager.get_page("tender"),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# TENDER SINGLE — با pid + slug
# =====================================================
# app_tender/views.py — فقط tender_single

def tender_single(request, slug: str):
    """
    فارسی:    /tender/نام-مناقصه/
    انگلیسی:  /en/tender/tender-name/
    """
    is_english = is_english_request(request)

    if is_english:
        tender = get_object_or_404(
            Tender.objects.select_related("category"),
            slug_en=slug,
        )
    else:
        tender = get_object_or_404(
            Tender.objects.select_related("category"),
            slug=slug,
        )

    template_name = (
        "LTR/tender/tender-single.html"
        if is_english
        else "RTL/tender/tender-single.html"
    )

    context = {
        "tender": tender,
        "seo": SEOManager.get_object(tender),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# TENDER SINGLE REDIRECT — از URL قدیمی /tender/5/
# =====================================================
def tender_single_redirect(request, pid):
    is_english = is_english_request(request)

    tender = get_object_or_404(Tender, pk=pid)

    if is_english:
        target = "app_tender_en:tender_single_en"
        redirect_slug = tender.slug_en or tender.slug
    else:
        target = "app_tender:tender_single"
        redirect_slug = tender.slug

    return redirect(target, pid=pid, slug=redirect_slug, permanent=True)


# =====================================================
# TENDER SEARCH
# =====================================================
def tender_search(request):
    is_english = is_english_request(request)

    query = request.GET.get("s", "").strip()

    tenders_qs = Tender.objects.all()

    if query:
        tenders_qs = tenders_qs.filter(
            Q(description_fa__icontains=query) |
            Q(description_en__icontains=query) |
            Q(title_fa__icontains=query) |
            Q(title_en__icontains=query)
        )

    tenders = paginate_queryset(request, tenders_qs)

    template_name = (
        "LTR/tender/tender-home.html"
        if is_english
        else "RTL/tender/tender-home.html"
    )

    context = {
        "tenders": tenders,
        "search_query": query,
        "seo": SEOManager.get_page("tender"),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# TENDER TAG
# =====================================================
def tender_tag(request, slug):
    is_english = is_english_request(request)

    if is_english:
        tag = get_object_or_404(TenderTag, slug_en=slug)
    else:
        tag = get_object_or_404(TenderTag, slug=slug)

    tenders_qs = Tender.objects.filter(tags=tag).order_by("-created_at_fa")
    tenders = paginate_queryset(request, tenders_qs)

    template_name = (
        "LTR/tender/tender-home.html"
        if is_english
        else "RTL/tender/tender-home.html"
    )

    context = {
        "tag": tag,
        "tenders": tenders,
        "seo": SEOManager.get_page("tender"),
        "is_english": is_english,
    }

    return render(request, template_name, context)