from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import models
from app_product.models import ProductCategory
from django.db.models import Count, Q
from app_blog.models import blog, blog_Tag
from app_banner.models import OtherBanner
from app_reports.models import FollowUsLink, SiteMainInfo


def get_common_context():
    """
    داده‌های مشترک تمام صفحات بلاگ
    """
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
        )
    }


def blog_home(request, cat_name=None, author_username=None):
    blogs = (
        blog.objects
        .filter(status="published")
        .order_by("-publish_date_fa", "order")
    )

    if cat_name:
        blogs = blogs.filter(category__title_fa=cat_name)

    if author_username:
        blogs = blogs.filter(author__username=author_username)

    paginator = Paginator(blogs, 8)
    page_number = request.GET.get("page")

    try:
        blogs = paginator.get_page(page_number)
    except PageNotAnInteger:
        blogs = paginator.get_page(1)
    except EmptyPage:
        blogs = paginator.get_page(paginator.num_pages)

    context = {
        "blogs": blogs,
        **get_common_context(),
    }

    return render(request, "RTL/blog/blog-home.html", context)


def blog_single(request, pid):
    blog_obj = get_object_or_404(
        blog.objects.filter(status="published"),
        pk=pid
    )

    context = {
        "blog": blog_obj,
        **get_common_context(),
    }

    return render(request, "RTL/blog/blog-single.html", context)


def blog_search(request):
    blogs_queryset = (
        blog.objects
        .filter(status="published")
        .select_related("author", "category")
    )

    s = request.GET.get("s", "").strip()

    if s:
        blogs_queryset = blogs_queryset.filter(
            models.Q(title_fa__icontains=s)
            | models.Q(title_en__icontains=s)
            | models.Q(content_1_fa__icontains=s)
            | models.Q(content_1_en__icontains=s)
            | models.Q(content_2_fa__icontains=s)
            | models.Q(content_2_en__icontains=s)
        )

    paginator = Paginator(blogs_queryset, 8)
    page_number = request.GET.get("page")

    try:
        blogs = paginator.get_page(page_number)
    except PageNotAnInteger:
        blogs = paginator.get_page(1)
    except EmptyPage:
        blogs = paginator.get_page(paginator.num_pages)

    context = {
        "blogs": blogs,
        "search_term": s,
        **get_common_context(),
    }

    return render(request, "RTL/blog/blog-home.html", context)


def blog_tag(request, slug):
    tag = get_object_or_404(blog_Tag, slug=slug)

    blogs_queryset = (
        blog.objects
        .filter(status="published", tags=tag)
        .select_related("author", "category")
    )

    paginator = Paginator(blogs_queryset, 8)
    page_number = request.GET.get("page")

    try:
        blogs = paginator.get_page(page_number)
    except PageNotAnInteger:
        blogs = paginator.get_page(1)
    except EmptyPage:
        blogs = paginator.get_page(paginator.num_pages)

    context = {
        "tag": tag,
        "blogs": blogs,
        **get_common_context(),
    }

    return render(request, "RTL/blog/blog-home.html", context)
