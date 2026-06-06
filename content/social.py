import os
import time
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.utils import timezone


FACEBOOK_GRAPH_VERSION = os.getenv("FACEBOOK_GRAPH_VERSION", "v24.0")


class FacebookPublishError(Exception):
    pass


class InstagramPublishError(Exception):
    pass


def get_public_page_url(page, request=None):
    base_url = os.getenv("PUBLIC_SITE_URL")
    if base_url:
        return urljoin(base_url.rstrip("/") + "/", page.url.lstrip("/"))

    if page.full_url:
        return page.full_url

    if request is not None:
        return request.build_absolute_uri(page.url)

    base_url = settings.WAGTAILADMIN_BASE_URL
    return urljoin(base_url.rstrip("/") + "/", page.url.lstrip("/"))


def get_public_media_url(path):
    base_url = os.getenv("PUBLIC_SITE_URL") or settings.WAGTAILADMIN_BASE_URL
    return urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def build_facebook_message(page):
    message_parts = [page.title]

    if page.teaser:
        message_parts.append(page.teaser)

    return "\n\n".join(message_parts)


def get_facebook_backdate_params(page):
    post_date = getattr(page, "date", None)

    if not post_date or post_date >= timezone.localdate():
        return {}

    return {
        "backdated_time": post_date.isoformat(),
        "backdated_time_granularity": "day",
    }


def build_instagram_caption(page, request=None):
    caption_parts = [page.title]

    if page.teaser:
        caption_parts.append(page.teaser)

    caption_parts.append(get_public_page_url(page, request))

    return "\n\n".join(caption_parts)


def refresh_facebook_link_preview(url, access_token):
    response = requests.post(
        f"https://graph.facebook.com/{FACEBOOK_GRAPH_VERSION}/",
        data={
            "id": url,
            "scrape": "true",
            "access_token": access_token,
        },
        timeout=15,
    )

    parse_graph_response(response, FacebookPublishError)


def publish_page_to_facebook(page, request=None):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    access_token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

    if not page_id or not access_token:
        raise FacebookPublishError(
            "FACEBOOK_PAGE_ID und FACEBOOK_PAGE_ACCESS_TOKEN muessen gesetzt sein."
        )

    page_url = get_public_page_url(page, request)
    refresh_facebook_link_preview(page_url, access_token)

    response = requests.post(
        f"https://graph.facebook.com/{FACEBOOK_GRAPH_VERSION}/{page_id}/feed",
        data={
            "message": build_facebook_message(page),
            "link": page_url,
            "access_token": access_token,
            **get_facebook_backdate_params(page),
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


def get_instagram_image_url(page):
    if not page.hero_image_id:
        raise InstagramPublishError("Instagram benoetigt ein Titelbild.")

    rendition = page.hero_image.get_rendition("max-1080x1350|format-jpeg|jpegquality-90")
    return get_public_media_url(rendition.url)


def publish_page_to_instagram(page, request=None):
    instagram_user_id = os.getenv("INSTAGRAM_USER_ID")
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not instagram_user_id or not access_token:
        raise InstagramPublishError(
            "INSTAGRAM_USER_ID und INSTAGRAM_ACCESS_TOKEN muessen gesetzt sein."
        )

    create_response = requests.post(
        f"https://graph.facebook.com/{FACEBOOK_GRAPH_VERSION}/{instagram_user_id}/media",
        data={
            "image_url": get_instagram_image_url(page),
            "caption": build_instagram_caption(page, request),
            "access_token": access_token,
        },
        timeout=30,
    )
    create_payload = parse_graph_response(create_response, InstagramPublishError)
    creation_id = create_payload.get("id")

    if not creation_id:
        raise InstagramPublishError(f"Instagram-Antwort ohne Creation-ID: {create_payload}")

    wait_for_instagram_container(creation_id, access_token)

    publish_response = requests.post(
        f"https://graph.facebook.com/{FACEBOOK_GRAPH_VERSION}/{instagram_user_id}/media_publish",
        data={
            "creation_id": creation_id,
            "access_token": access_token,
        },
        timeout=30,
    )
    publish_payload = parse_graph_response(publish_response, InstagramPublishError)
    media_id = publish_payload.get("id")

    if not media_id:
        raise InstagramPublishError(f"Instagram-Antwort ohne Media-ID: {publish_payload}")

    return media_id


def wait_for_instagram_container(creation_id, access_token, attempts=6, delay=2):
    last_payload = None

    for _ in range(attempts):
        response = requests.get(
            f"https://graph.facebook.com/{FACEBOOK_GRAPH_VERSION}/{creation_id}",
            params={
                "fields": "status_code,status",
                "access_token": access_token,
            },
            timeout=15,
        )
        payload = parse_graph_response(response, InstagramPublishError)
        last_payload = payload
        status_code = payload.get("status_code")

        if status_code == "FINISHED":
            return

        if status_code in {"ERROR", "EXPIRED"}:
            message = payload.get("status") or status_code
            raise InstagramPublishError(f"Instagram-Media-Container konnte nicht verarbeitet werden: {message}")

        time.sleep(delay)

    raise InstagramPublishError(
        f"Instagram-Media-Container ist noch nicht bereit: {last_payload}"
    )


def parse_graph_response(response, error_class):
    try:
        payload = response.json()
    except ValueError as error:
        raise error_class(
            f"Meta hat keine gueltige JSON-Antwort geliefert: {response.text[:500]}"
        ) from error

    if response.status_code >= 400 or "error" in payload:
        error_payload = payload.get("error", payload)
        message = error_payload.get("message", str(error_payload))
        raise error_class(message)

    return payload
