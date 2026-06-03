import os
from urllib.parse import urljoin

import requests
from django.conf import settings


FACEBOOK_GRAPH_VERSION = os.getenv("FACEBOOK_GRAPH_VERSION", "v24.0")


class FacebookPublishError(Exception):
    pass


def get_public_page_url(page, request=None):
    if page.full_url:
        return page.full_url

    if request is not None:
        return request.build_absolute_uri(page.url)

    base_url = os.getenv("PUBLIC_SITE_URL") or settings.WAGTAILADMIN_BASE_URL
    return urljoin(base_url.rstrip("/") + "/", page.url.lstrip("/"))


def build_facebook_message(page):
    message_parts = [page.title]

    if page.teaser:
        message_parts.append(page.teaser)

    return "\n\n".join(message_parts)


def publish_page_to_facebook(page, request=None):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

    if not page_id or not access_token:
        raise FacebookPublishError(
            "FACEBOOK_PAGE_ID und FACEBOOK_PAGE_ACCESS_TOKEN muessen gesetzt sein."
        )

    response = requests.post(
        f"https://graph.facebook.com/{FACEBOOK_GRAPH_VERSION}/{page_id}/feed",
        data={
            "message": build_facebook_message(page),
            "link": get_public_page_url(page, request),
            "access_token": access_token,
        },
        timeout=15,
    )

    try:
        payload = response.json()
    except ValueError as error:
        raise FacebookPublishError(
            f"Facebook hat keine gueltige JSON-Antwort geliefert: {response.text[:500]}"
        ) from error

    if response.status_code >= 400 or "error" in payload:
        error_payload = payload.get("error", payload)
        message = error_payload.get("message", str(error_payload))
        raise FacebookPublishError(message)

    post_id = payload.get("id")
    if not post_id:
        raise FacebookPublishError(f"Facebook-Antwort ohne Post-ID: {payload}")

    return post_id
