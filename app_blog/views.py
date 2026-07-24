# app_blog/views.py

from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models

from app_blog.models import blog, blog_Tag
from app_seo.utils import SEOManager


# =====================================================
# BLOG HOME
# =====================================================
def blog_home(request, cat_name=None, author_username=None):

    blogs_queryset = (
        blog.objects
        .filter(status="published")
        .order_by("-publish_date_fa", "order")
    )

    if cat_name:
        blogs_queryset = blogs_queryset.filter(
            category__title_fa=cat_name
        )

    if author_username:
        blogs_queryset = blogs_queryset.filter(
            author__username=author_username
        )

    paginator = Paginator(
        blogs_queryset,
        8
    )

    page_number = request.GET.get("page")

    try:
        blogs = paginator.get_page(page_number)

    except PageNotAnInteger:
        blogs = paginator.get_page(1)

    except EmptyPage:
        blogs = paginator.get_page(
            paginator.num_pages
        )

    context = {
        "blogs": blogs,
        "seo": SEOManager.get_page("blog"),
    }

    return render(
        request,
        "RTL/blog/blog-home.html",
        context
    )


# =====================================================
# BLOG SINGLE
# =====================================================
def blog_single(request, pid):

    blog_obj = get_object_or_404(
        blog.objects.filter(
            status="published"
        ),
        pk=pid
    )

    context = {
        "blog": blog_obj,
        "seo": SEOManager.get_object(blog_obj),
    }

    return render(
        request,
        "RTL/blog/blog-single.html",
        context
    )


# =====================================================
# BLOG SEARCH
# =====================================================
def blog_search(request):

    blogs_queryset = (
        blog.objects
        .filter(status="published")
        .select_related(
            "author",
            "category"
        )
    )

    s = request.GET.get(
        "s",
        ""
    ).strip()

    if s:
        blogs_queryset = blogs_queryset.filter(

            models.Q(title_fa__icontains=s)
            |
            models.Q(title_en__icontains=s)
            |
            models.Q(content_1_fa__icontains=s)
            |
            models.Q(content_1_en__icontains=s)
            |
            models.Q(content_2_fa__icontains=s)
            |
            models.Q(content_2_en__icontains=s)

        )

    paginator = Paginator(
        blogs_queryset,
        8
    )

    page_number = request.GET.get("page")

    try:
        blogs = paginator.get_page(page_number)

    except PageNotAnInteger:
        blogs = paginator.get_page(1)

    except EmptyPage:
        blogs = paginator.get_page(
            paginator.num_pages
        )

    context = {
        "blogs": blogs,
        "search_term": s,
        "seo": SEOManager.get_page("blog_search"),
    }

    return render(
        request,
        "RTL/blog/blog-home.html",
        context
    )


# =====================================================
# BLOG TAG
# =====================================================
def blog_tag(request, slug):

    tag = get_object_or_404(
        blog_Tag,
        slug=slug
    )

    blogs_queryset = (
        blog.objects
        .filter(
            status="published",
            tags=tag
        )
        .select_related(
            "author",
            "category"
        )
    )

    paginator = Paginator(
        blogs_queryset,
        8
    )

    page_number = request.GET.get("page")

    try:
        blogs = paginator.get_page(page_number)

    except PageNotAnInteger:
        blogs = paginator.get_page(1)

    except EmptyPage:
        blogs = paginator.get_page(
            paginator.num_pages
        )

    context = {
        "tag": tag,
        "blogs": blogs,
        "seo": SEOManager.get_page("blog_tag"),
    }

    return render(
        request,
        "RTL/blog/blog-home.html",
        context
    )