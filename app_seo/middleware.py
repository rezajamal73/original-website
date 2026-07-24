from .utils import SEOManager


class SEOMiddleware:


    def __init__(self, get_response):

        self.get_response = get_response



    def __call__(self, request):

        request.seo = None


        resolver = getattr(
            request,
            "resolver_match",
            None
        )


        if resolver:


            # =========================
            # صفحات ثابت
            # =========================

            request.seo = SEOManager.get_page(
                resolver.url_name
            )



            # =========================
            # صفحات داینامیک
            # =========================

            if not request.seo:


                obj = self.get_object_from_view(
                    resolver
                )


                if obj:

                    request.seo = SEOManager.get_object(
                        obj
                    )



        response = self.get_response(
            request
        )


        return response




    def get_object_from_view(
        self,
        resolver
    ):


        kwargs = resolver.kwargs


        object_id = (

            kwargs.get("pk")

            or

            kwargs.get("id")

            or

            kwargs.get("pid")

        )


        if not object_id:

            return None



        try:


            view_func = resolver.func



            # برای Class Based View

            view_class = getattr(
                view_func,
                "view_class",
                None
            )


            if view_class:


                queryset = view_class.get_queryset()


                return queryset.filter(
                    pk=object_id
                ).first()



        except Exception:


            pass



        return None