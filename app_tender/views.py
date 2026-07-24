from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from app_tender.models import Tender, TenderTag
from app_seo.utils import SEOManager




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
    tenders_qs = Tender.objects.all().order_by("-created_at_fa")

    if cat_name:
        tenders_qs = tenders_qs.filter(category__title_fa=cat_name).order_by("-created_at_fa")

    if author_username:
        tenders_qs = tenders_qs.filter(author__username=author_username).order_by("-created_at_fa")

    tenders = paginate_queryset(request, tenders_qs)

    context = {
        "tenders": tenders,
        "seo": SEOManager.get_page("tender"),
    }
    return render(request, "RTL/tender/tender-home.html", context)



# =====================================================
# TENDER SINGLE
# =====================================================
def tender_single(request, pid):
    tender = get_object_or_404(Tender, pk=pid)

    context = {
        "tender": tender,
        "seo": SEOManager.get_object(tender),
    }
    return render(request, "RTL/tender/tender-single.html", context)


# =====================================================
# TENDER SEARCH
# =====================================================
def tender_search(request):
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

    context = {
        "tenders": tenders,
        "search_query": query,
        "seo": SEOManager.get_page("tender"),
    }
    return render(request, "RTL/tender/tender-home.html", context)


# =====================================================
# TENDER TAG
# =====================================================
def tender_tag(request, slug):
    tag = get_object_or_404(TenderTag, slug=slug)

    tenders_qs = Tender.objects.filter(tags=tag).order_by("-created_at_fa")
    tenders = paginate_queryset(request, tenders_qs)

    context = {
        "tag": tag,
        "tenders": tenders,
        "seo": SEOManager.get_page("tender"),
    }
    return render(request, "RTL/tender/tender-home.html", context)