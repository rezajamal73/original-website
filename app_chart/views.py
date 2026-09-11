
# app_chart/views.py

from django.shortcuts import render, get_object_or_404

from app_chart.models import Person, BoardMember
from app_seo.utils import SEOManager


# =====================================================
# LANGUAGE DETECTION
# =====================================================

def is_english_request(request):
    """
    Detect English pages based on URL name.

    Persian:
        chart
        person_detail
        board_home
        board_single

    English:
        chart_en
        person_detail_en
        board_home_en
        board_single_en
    """

    url_name = getattr(
        request.resolver_match,
        "url_name",
        ""
    )

    return url_name.endswith("_en")


# =====================================================
# ORGANIZATION CHART
# =====================================================

def orgchart_tree(request):

    is_english = is_english_request(request)

    ceo_list = (
        Person.objects
        .filter(is_ceo=True)
        .order_by("order")
    )

    if not ceo_list.exists():

        ceo_list = (
            Person.objects
            .filter(parent__isnull=True)
            .order_by("order")
        )

    template_name = (
        "LTR/chart/chart_home.html"
        if is_english
        else "RTL/chart/chart_home.html"
    )

    context = {
        "ceo_list": ceo_list,
        "seo": SEOManager.get_page("chart"),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context
    )


# =====================================================
# PERSON DETAIL
# =====================================================

def person_detail(request, pid):

    is_english = is_english_request(request)

    person = get_object_or_404(
        Person,
        pk=pid
    )

    template_name = (
        "LTR/chart/person_detail.html"
        if is_english
        else "RTL/chart/person_detail.html"
    )

    context = {
        "person": person,
        "seo": SEOManager.get_object(person),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context
    )


# =====================================================
# BOARD MEMBER LIST
# =====================================================

def board_home(request):

    is_english = is_english_request(request)

    board_list = (
        BoardMember.objects
        .filter(parent__isnull=True)
        .order_by("order")
    )

    template_name = (
        "LTR/chart/board_home.html"
        if is_english
        else "RTL/chart/board_home.html"
    )

    context = {
        "board_list": board_list,
        "seo": SEOManager.get_page("chart"),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context
    )


# =====================================================
# BOARD MEMBER DETAIL
# =====================================================

def board_single(request, pid):

    is_english = is_english_request(request)

    member = get_object_or_404(
        BoardMember,
        pk=pid
    )

    template_name = (
        "LTR/chart/board_single.html"
        if is_english
        else "RTL/chart/board_single.html"
    )

    context = {
        "member": member,
        "seo": SEOManager.get_object(member),
        "is_english": is_english,
    }

    return render(
        request,
        template_name,
        context
    )

