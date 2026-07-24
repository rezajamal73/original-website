from .utils import SEOManager


def seo(request):

    seo = None


    resolver = request.resolver_match


    if resolver:


        url_name = resolver.url_name


        # -------------------------
        # صفحات ثابت
        # -------------------------

        seo = SEOManager.get_page(
            url_name
        )


        # -------------------------
        # صفحات داینامیک
        # -------------------------

        if not seo:


            view_kwargs = resolver.kwargs


            obj = None


            # معمولا pk
            object_id = (
                view_kwargs.get("pk")
                or
                view_kwargs.get("id")
                or
                view_kwargs.get("pid")
            )


            if object_id:


                # پیدا کردن object از view context
                try:

                    view_class = resolver.func.view_class

                    queryset = view_class.get_queryset()

                    obj = queryset.filter(
                        pk=object_id
                    ).first()


                except Exception:

                    obj = None



            if obj:

                seo = SEOManager.get_object(
                    obj
                )



    return {

        "seo": seo

    }