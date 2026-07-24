from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.http import HttpRequest
from django.db.models import Q

from app_product.models import Product, ProductTag, ProductScan
from app_seo.utils import SEOManager


# =====================================================
# PRODUCT LIST (CATEGORY FILTER)
# =====================================================

def product_list(request, slug=None):

    products_qs = (
        Product.objects
        .filter(status="published")
        .select_related("category", "category2")
        .order_by("priority", "title_fa")
    )

    if slug:
        products_qs = products_qs.filter(category__slug=slug)

    paginator = Paginator(products_qs, 8)
    products = paginator.get_page(request.GET.get("page"))

    context = {
        "products": products,
        "query": "",
        "seo": SEOManager.get_page("products"),
    }

    return render(
        request,
        "RTL/product/product_home.html",
        context
    )


# =====================================================
# PRODUCT LIST BY FORM
# =====================================================

def product_list_by_form(request, slug):

    products_qs = (
        Product.objects
        .filter(
            status="published",
            category2__slug=slug
        )
        .select_related("category", "category2")
        .order_by("priority", "title_fa")
    )

    paginator = Paginator(products_qs, 8)
    products = paginator.get_page(request.GET.get("page"))

    context = {
        "products": products,
        "query": "",
        "seo": SEOManager.get_page("products"),
    }

    return render(
        request,
        "RTL/product/product_home.html",
        context
    )


# =====================================================
# PRODUCT SEARCH
# =====================================================

def product_search(request):

    query = request.GET.get("q", "").strip()

    products_qs = (
        Product.objects
        .filter(status="published")
        .select_related("category", "category2")
        .order_by("priority", "title_fa")
    )

    if query:
        products_qs = products_qs.filter(
            Q(title_fa__icontains=query) |
            Q(title_en__icontains=query) |
            Q(generic_name_fa__icontains=query) |
            Q(generic_name_en__icontains=query) |
            Q(sku__icontains=query) |
            Q(summary_fa__icontains=query) |
            Q(summary_en__icontains=query)
        ).distinct()

    paginator = Paginator(products_qs, 8)
    products = paginator.get_page(request.GET.get("page"))

    context = {
        "products": products,
        "query": query,
        "seo": SEOManager.get_page("products"),
    }

    return render(
        request,
        "RTL/product/product_home.html",
        context
    )


# =====================================================
# PRODUCT TAG
# =====================================================

def product_tag(request, slug):

    tag = get_object_or_404(
        ProductTag,
        slug=slug
    )

    products_qs = (
        Product.objects
        .filter(
            tags=tag,
            status="published"
        )
        .select_related("category")
        .order_by("priority", "title_fa")
    )

    paginator = Paginator(products_qs, 8)
    products = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "tag": tag,
        "products": products,
        "query": "",
        "seo": SEOManager.get_page("products"),
    }

    return render(
        request,
        "RTL/product/product_home.html",
        context
    )


# =====================================================
# PRODUCT SINGLE
# =====================================================

def product_single(request, pid: int):

    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=pid,
        status="published"
    )

    context = {
        "product": product,
        "seo": SEOManager.get_object(product),
    }

    return render(
        request,
        "RTL/product/product_single.html",
        context
    )


# =====================================================
# QR SCAN TRACKING
# =====================================================

def scan_product(request: HttpRequest, sku: str):

    product = get_object_or_404(
        Product,
        sku=sku
    )

    ip = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if ip:
        ip = ip.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")

    user_agent = request.META.get(
        "HTTP_USER_AGENT",
        ""
    )

    ProductScan.objects.create(
        product=product,
        ip_address=ip,
        user_agent=user_agent
    )

    return redirect(
        product.get_absolute_url()
    )