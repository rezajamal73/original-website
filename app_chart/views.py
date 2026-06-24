from django.shortcuts import render, get_object_or_404
from app_chart.models import Person, BoardMember
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo
from app_product.models import ProductCategory
from django.db.models import Count, Q


# -------------------------------------------------
#  Context مشترک
# -------------------------------------------------
def get_common_context():
    return {
        "categories": (
        ProductCategory.objects
        .annotate(
            product_count=Count(
                "products",
                filter=Q(products__status="published")
            )
        )
        .filter(product_count__gt=0)
        .order_by("priority", "title_fa")),
        "site_info": SiteMainInfo.objects.first(),
        "banner": OtherBanner.objects.filter(status="published").first(),
        "follow_links": (
            FollowUsLink.objects
            .filter(is_active=True, svg_icon__isnull=False)
            .exclude(url="")
            .order_by("display_order")
        ),
    }


# -------------------------------------------------
#  چارت سازمانی
# -------------------------------------------------
def orgchart_tree(request):
    ceo_list = Person.objects.filter(is_ceo=True).order_by("order")

    if not ceo_list.exists():
        ceo_list = Person.objects.filter(parent__isnull=True).order_by("order")

    context = {
        "ceo_list": ceo_list,
        **get_common_context(),
    }

    return render(request, "RTL/chart/chart_home.html", context)


def person_detail(request, pid):
    person = get_object_or_404(Person, pk=pid)

    context = {
        "person": person,
        **get_common_context(),
    }

    return render(request, "RTL/chart/person_detail.html", context)


# -------------------------------------------------
#  هیأت‌مدیره
# -------------------------------------------------
def board_home(request):
    board_list = BoardMember.objects.filter(parent__isnull=True).order_by("order")

    context = {
        "board_list": board_list,
        **get_common_context(),
    }

    return render(request, "RTL/chart/board_home.html", context)


def board_single(request, pid):
    member = get_object_or_404(BoardMember, pk=pid)

    context = {
        "member": member,
        **get_common_context(),
    }

    return render(request, "RTL/chart/board_single.html", context)
