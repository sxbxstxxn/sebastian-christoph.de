import os
from urllib.parse import urljoin

from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag(takes_context=True)
def absolute_url(context, path):
    base_url = os.getenv("PUBLIC_SITE_URL")
    if base_url:
        return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))

    request = context.get("request")
    if request is not None:
        return request.build_absolute_uri(path)

    return urljoin(settings.WAGTAILADMIN_BASE_URL.rstrip("/") + "/", path.lstrip("/"))
