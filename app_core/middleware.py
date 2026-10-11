# app_core/middleware.py

from urllib.parse import unquote
from django.urls import set_script_prefix


class DecodePathInfoMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_script_prefix("")
        request.META["SCRIPT_NAME"] = ""

        path_info = request.path_info or ""
        if "%" in path_info:
            try:
                decoded = unquote(path_info)
                if decoded != path_info:
                    if not decoded.startswith("/"):
                        decoded = "/" + decoded
                    request.path_info = decoded
                    request.META["PATH_INFO"] = decoded
                    request.__dict__.pop("_path", None)
            except Exception:
                pass

        return self.get_response(request)