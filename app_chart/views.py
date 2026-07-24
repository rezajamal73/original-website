# app_chart/views.py

from django.shortcuts import render, get_object_or_404

from app_chart.models import Person, BoardMember
from app_seo.utils import SEOManager



# =====================================================
# ORGANIZATION CHART
# =====================================================
def orgchart_tree(request):

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


    context = {
        "ceo_list": ceo_list,
        "seo": SEOManager.get_page("chart"),
    }


    return render(
        request,
        "RTL/chart/chart_home.html",
        context
    )



# =====================================================
# PERSON DETAIL
# =====================================================
def person_detail(request, pid):

    person = get_object_or_404(
        Person,
        pk=pid
    )


    context = {
        "person": person,
        "seo": SEOManager.get_object(person),
    }


    return render(
        request,
        "RTL/chart/person_detail.html",
        context
    )



# =====================================================
# BOARD MEMBER LIST
# =====================================================
def board_home(request):

    board_list = (
        BoardMember.objects
        .filter(parent__isnull=True)
        .order_by("order")
    )


    context = {
        "board_list": board_list,
        "seo": SEOManager.get_page("chart"),
    }


    return render(
        request,
        "RTL/chart/board_home.html",
        context
    )



# =====================================================
# BOARD MEMBER DETAIL
# =====================================================
def board_single(request, pid):

    member = get_object_or_404(
        BoardMember,
        pk=pid
    )


    context = {
        "member": member,
        "seo": SEOManager.get_object(member),
    }


    return render(
        request,
        "RTL/chart/board_single.html",
        context
    )