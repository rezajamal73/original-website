from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db import models

from app_blog.models import blog, blog_Tag
from app_seo.utils import SEOManager


# =====================================================
# LANGUAGE DETECTION
# =====================================================

def is_english_request(request):
    """
    Detect English blog URLs based on the URL name.

    Persian:
        blog_home
        blog_single
        search
        blog_tag

    English:
        blog_home_en
        blog_single_en
        search_en
        blog_tag_en
    """

    url_name = getattr(
        request.resolver_match,
        "url_name",
        ""
    )

    return url_name.endswith("_en")


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

    blogs_queryset = (
        blog.objects
        .filter(status="published")
        .select_related("category", "author")
        .order_by("-publish_date_fa", "order")
    )

    # -------------------------------------------------
    # Category
    # -------------------------------------------------

    if slug:
        blogs_queryset = blogs_queryset.filter(
            category__slug=slug
        )

    # -------------------------------------------------
    # Author
    # -------------------------------------------------

    if author_username:
        blogs_queryset = blogs_queryset.filter(
            author__username=author_username
        )

    # -------------------------------------------------
    # Pagination
    # -------------------------------------------------

    paginator = Paginator(
        blogs_queryset,
        8
    )

    page_number = request.GET.get("page")

    blogs = paginator.get_page(
        page_number
    )

    # -------------------------------------------------
    # Context
    # -------------------------------------------------

    context = {
        "blogs": blogs,
        "seo": SEOManager.get_page("blog"),
        "is_english": is_english,
    }

    return render(
        request,
        template,
        context
    )


# =====================================================
# BLOG SINGLE
# =====================================================

def blog_single(request, pid):

    is_english = is_english_request(request)

    template = (
        "LTR/blog/blog-single.html"
        if is_english
        else "RTL/blog/blog-single.html"
    )

    blog_obj = get_object_or_404(
        blog.objects.filter(
            status="published"
        ),
        pk=pid
    )

    context = {
        "blog": blog_obj,
        "seo": SEOManager.get_object(
            blog_obj
        ),
        "is_english": is_english,
    }

    return render(
        request,
        template,
        context
    )


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
        .select_related(
            "author",
            "category"
        )
    )

    s = request.GET.get(
        "s",
        ""
    ).strip()

    # -------------------------------------------------
    # Search
    # -------------------------------------------------

    if s:

        blogs_queryset = blogs_queryset.filter(

            models.Q(
                title_fa__icontains=s
            )

            |

            models.Q(
                title_en__icontains=s
            )

            |

            models.Q(
                content_1_fa__icontains=s
            )

            |

            models.Q(
                content_1_en__icontains=s
            )

            |

            models.Q(
                content_2_fa__icontains=s
            )

            |

            models.Q(
                content_2_en__icontains=s
            )
        )

    # -------------------------------------------------
    # Pagination
    # -------------------------------------------------

    paginator = Paginator(
        blogs_queryset,
        8
    )

    page_number = request.GET.get(
        "page"
    )

    blogs = paginator.get_page(
        page_number
    )

    # -------------------------------------------------
    # Context
    # -------------------------------------------------

    context = {
        "blogs": blogs,
        "search_term": s,
        "seo": SEOManager.get_page(
            "blog_search"
        ),
        "is_english": is_english,
    }

    return render(
        request,
        template,
        context
    )


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

    # -------------------------------------------------
    # Pagination
    # -------------------------------------------------

    paginator = Paginator(
        blogs_queryset,
        8
    )

    page_number = request.GET.get(
        "page"
    )

    blogs = paginator.get_page(
        page_number
    )

    # -------------------------------------------------
    # Context
    # -------------------------------------------------

    context = {
        "tag": tag,
        "blogs": blogs,
        "seo": SEOManager.get_page(
            "blog_tag"
        ),
        "is_english": is_english,
    }

    return render(
        request,
        template,
        context
    )