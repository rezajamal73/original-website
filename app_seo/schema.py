import json



def generate_schema(seo, obj=None):


    if seo and seo.schema_json:

        return seo.schema_json



    if not seo:

        return {}



    base = {

        "@context": "https://schema.org",

    }



    # =====================
    # Organization
    # =====================

    if seo.content_type == "page":


        base.update({

            "@type": "Organization",

            "name": seo.title,

            "description": seo.description,

        })



    # =====================
    # Product
    # =====================

    elif seo.content_type == "product":


        base.update({

            "@type": "Product",

            "name": seo.title,

            "description": seo.description,

        })


        if obj:

            if hasattr(obj, "image"):

                if obj.image:

                    base["image"] = obj.image.url



    # =====================
    # Article
    # =====================

    elif seo.content_type == "blog":


        base.update({

            "@type": "Article",

            "headline": seo.title,

            "description": seo.description,

        })



    # =====================
    # News
    # =====================

    elif seo.content_type == "news":


        base.update({

            "@type": "NewsArticle",

            "headline": seo.title,

            "description": seo.description,

        })



    # =====================
    # Resume
    # =====================

    elif seo.content_type == "resume":


        base.update({

            "@type": "CreativeWork",

            "name": seo.title,

            "description": seo.description,

        })



    return base