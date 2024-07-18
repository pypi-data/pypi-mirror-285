import json
from functools import wraps
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.templatetags.static import static

from .response import BaseResponse, RedirectResponse, ReloadResponse


def djangorender_view(fn):
    """
    Wraps a view to make it load with Django Render
    """

    @wraps(fn)
    def wrapper(request, *args, **kwargs):
        response = fn(request, *args, **kwargs)

        if response.status_code == 301:
            return response

        # If the request was made by Django Render
        # (using `fetch()`, rather than a regular browser request)
        if request.META.get("HTTP_X_REQUESTED_WITH") == "DjangoRender":
            if isinstance(response, BaseResponse):
                return response

            elif response.status_code == 302:
                return RedirectResponse(response["Location"])

            else:
                # Response couldn't be converted into a Django Render response. Reload the page
                return ReloadResponse()

        # Regular browser request
        # If the response is a Django Render response, wrap it in our bootstrap template
        # to load the React SPA and render the response data.
        if isinstance(response, BaseResponse):
            if settings.DJREAM_VITE_BUNDLE_DIR:
                # Production - Use asset manifest to find URLs to bundled JS/CSS
                asset_manifest = json.loads(
                    (
                        Path(settings.DJREAM_VITE_BUNDLE_DIR) / ".vite/manifest.json"
                    ).read_text()
                )

                js = [
                    static(asset_manifest["src/main.tsx"]["file"]),
                ]
                css = asset_manifest["src/main.tsx"]["css"]
                vite_react_refresh_runtime = None

            elif settings.DJREAM_VITE_DEVSERVER_URL:
                # Development - Fetch JS/CSS from Vite server
                js = [
                    settings.DJREAM_VITE_DEVSERVER_URL + "/@vite/client",
                    settings.DJREAM_VITE_DEVSERVER_URL + "/src/main.tsx",
                ]
                css = []
                vite_react_refresh_runtime = (
                    settings.DJREAM_VITE_DEVSERVER_URL + "/@react-refresh"
                )

            else:
                raise ImproperlyConfigured(
                    "DJREAM_VITE_BUNDLE_DIR (production) or DJREAM_VITE_DEVSERVER_URL (development) must be set"
                )

            # Wrap the response with our bootstrap template
            new_response = render(
                request,
                "djangorender/bootstrap.html",
                {
                    "data": response.content.decode("utf-8"),
                    "js": js,
                    "css": css,
                    "vite_react_refresh_runtime": vite_react_refresh_runtime,
                },
            )

            # Copy status_code and cookies from the original response
            new_response.status_code = response.status_code
            new_response.cookies = response.cookies

            return new_response

        return response

    return wrapper
