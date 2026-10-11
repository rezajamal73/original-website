from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db import models

from app_blog.models import blog, blog_Tag
from app_seo.utils import SEOManager

from app_core.url_helpers import is_english_request


# =====================================================
# BLOG HOME
# =====================================================

def blog_home(request, slug=None, author_username=None):

    is_english = is_english_request(request)

    template = (
        "LTR/blog/blog-home.html"
        if is_english
        else "RTL/blog/blog-home.html"
    )

    # ==========================================
    # ✅ DEBUG
    # ==========================================
    print("=" * 60)
    print(f"🔍 DEBUG blog_home")
    print(f"   URL: {request.path}")
    print(f"   is_english: {is_english}")
    print(f"   slug: {slug!r}")
    print(f"   template: {template}")
    if request.resolver_match:
        print(f"   namespace: {request.resolver_match.namespace}")
        print(f"   url_name: {request.resolver_match.url_name}")

    # ==========================================
    # ✅ ساده: همه مقالات منتشرشده
    # ==========================================
    blogs_queryset = blog.objects.filter(status="published")
    print(f"   after status filter: {blogs_queryset.count()}")

    if slug:
        if is_english:
            blogs_queryset = blogs_queryset.filter(category__slug_en=slug)
        else:
            blogs_queryset = blogs_queryset.filter(category__slug=slug)
        print(f"   after slug filter: {blogs_queryset.count()}")

    if author_username:
        blogs_queryset = blogs_queryset.filter(author__username=author_username)
        print(f"   after author filter: {blogs_queryset.count()}")

    # ✅ ترتیب ساده
    blogs_queryset = blogs_queryset.order_by("-created_at_fa")
    print(f"   final count: {blogs_queryset.count()}")
    print("=" * 60)

    paginator = Paginator(blogs_queryset, 8)
    blogs = paginator.get_page(request.GET.get("page"))

    context = {
        "blogs": blogs,
        "seo": SEOManager.get_page("blog"),
        "is_english": is_english,
    }

    return render(request, template, context)


# =====================================================
# BLOG SINGLE — با pid + slug
# =====================================================

# app_blog/views.py — فقط blog_single

def blog_single(request, slug: str):
    """
    فارسی:    /blog/نام-مقاله/
    انگلیسی:  /en/blog/post-name/
    """
    is_english = is_english_request(request)

    if is_english:
        blog_obj = get_object_or_404(
            blog.objects.select_related("category"),
            slug_en=slug,
            status="published",
        )
    else:
        blog_obj = get_object_or_404(
            blog.objects.select_related("category"),
            slug=slug,
            status="published",
        )

    template_name = (
        "LTR/blog/blog-single.html"
        if is_english
        else "RTL/blog/blog-single.html"
    )

    context = {
        "blog": blog_obj,
        "seo": SEOManager.get_object(blog_obj),
        "is_english": is_english,
    }

    return render(request, template_name, context)


# =====================================================
# BLOG SINGLE REDIRECT — از URL قدیمی /blog/1/
# =====================================================

def blog_single_redirect(request, pid):

    is_english = is_english_request(request)

    blog_obj = get_object_or_404(blog, pk=pid, status="published")

    if is_english:
        target = "app_blog_en:blog_single_en"
        redirect_slug = blog_obj.slug_en or blog_obj.slug
    else:
        target = "app_blog:blog_single"
        redirect_slug = blog_obj.slug

    return redirect(target, pid=pid, slug=redirect_slug, permanent=True)


# =====================================================
# BLOG SEARCH
# =====================================================

def blog_search(request):

    is_english = is_english_request(request)

    template = (
        "LTR/blog/blog-home.html"
        if is_english
        else "RTL/blog/blog-home.html"
    )

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
    blogs = paginator.get_page(request.GET.get("page"))

    context = {
        "blogs": blogs,
        "search_term": s,
        "seo": SEOManager.get_page("blog_search"),
        "is_english": is_english,
    }

    return render(request, template, context)


# =====================================================
# BLOG TAG
# =====================================================

def blog_tag(request, slug):

    is_english = is_english_request(request)

    template = (
        "LTR/blog/blog-home.html"
        if is_english
        else "RTL/blog/blog-home.html"
    )

    if is_english:
        tag = get_object_or_404(blog_Tag, slug_en=slug)
    else:
        tag = get_object_or_404(blog_Tag, slug=slug)

    blogs_queryset = (
        blog.objects
        .filter(status="published", tags=tag)
        .select_related("author", "category")
    )

    paginator = Paginator(blogs_queryset, 8)
    blogs = paginator.get_page(request.GET.get("page"))

    context = {
        "tag": tag,
        "blogs": blogs,
        "seo": SEOManager.get_page("blog_tag"),
        "is_english": is_english,
    }

    return render(request, template, context)