from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path, reverse
from wagtail import hooks
from wagtail.admin.action_menu import ActionMenuItem
from wagtail.admin.auth import require_admin_access

from .models import BaseContentPage
from .social import (
    FacebookPublishError,
    InstagramPublishError,
    publish_page_to_facebook,
    publish_page_to_instagram,
)


class ResetFacebookPostIdMenuItem(ActionMenuItem):
    name = "reset-facebook-post-id"
    label = "Facebook-ID zuruecksetzen"

    def get_url(self, context):
        page = context.get("page")

        if not page:
            return None

        return reverse("content_admin_reset_facebook_post_id", args=[page.id])

    def is_shown(self, context):
        page = context.get("page")

        if not page:
            return False

        specific_page = page.specific
        return isinstance(specific_page, BaseContentPage) and bool(specific_page.facebook_post_id)


class ResetInstagramMediaIdMenuItem(ActionMenuItem):
    name = "reset-instagram-media-id"
    label = "Instagram-ID zuruecksetzen"

    def get_url(self, context):
        page = context.get("page")

        if not page:
            return None

        return reverse("content_admin_reset_instagram_media_id", args=[page.id])

    def is_shown(self, context):
        page = context.get("page")

        if not page:
            return False

        specific_page = page.specific
        return isinstance(specific_page, BaseContentPage) and bool(specific_page.instagram_media_id)


@hooks.register("register_page_action_menu_item")
def register_reset_facebook_post_id_menu_item():
    return ResetFacebookPostIdMenuItem(order=95)


@hooks.register("register_page_action_menu_item")
def register_reset_instagram_media_id_menu_item():
    return ResetInstagramMediaIdMenuItem(order=96)


@hooks.register("register_admin_urls")
def register_social_admin_urls():
    return [
        path(
            "pages/<int:page_id>/reset-facebook-post-id/",
            reset_facebook_post_id,
            name="content_admin_reset_facebook_post_id",
        ),
        path(
            "pages/<int:page_id>/reset-instagram-media-id/",
            reset_instagram_media_id,
            name="content_admin_reset_instagram_media_id",
        ),
    ]


@require_admin_access
def reset_facebook_post_id(request, page_id):
    page = get_object_or_404(BaseContentPage, pk=page_id)

    if request.method == "POST":
        BaseContentPage.objects.filter(pk=page_id).update(
            facebook_post_id="",
            facebook_last_error="",
        )
        messages.success(
            request,
            "Die Facebook Post-ID wurde zurueckgesetzt. Beim naechsten Veroeffentlichen kann der Beitrag erneut gepostet werden.",
        )
        return redirect("wagtailadmin_pages:edit", page_id)

    return render(
        request,
        "content/admin/reset_facebook_post_id.html",
        {"page": page},
    )


@require_admin_access
def reset_instagram_media_id(request, page_id):
    page = get_object_or_404(BaseContentPage, pk=page_id)

    if request.method == "POST":
        BaseContentPage.objects.filter(pk=page_id).update(
            instagram_media_id="",
            instagram_last_error="",
        )
        messages.success(
            request,
            "Die Instagram Media-ID wurde zurueckgesetzt. Beim naechsten Veroeffentlichen kann der Beitrag erneut gepostet werden.",
        )
        return redirect("wagtailadmin_pages:edit", page_id)

    return render(
        request,
        "content/admin/reset_instagram_media_id.html",
        {"page": page},
    )


@hooks.register("after_publish_page")
def publish_to_social_media_after_publish(request, page):
    specific_page = page.specific

    if not isinstance(specific_page, BaseContentPage):
        return

    update_fields = {}

    if specific_page.publish_to_facebook and not specific_page.facebook_post_id:
        update_fields["facebook_last_error"] = ""

        try:
            update_fields["facebook_post_id"] = publish_page_to_facebook(specific_page, request)
        except FacebookPublishError as error:
            update_fields["facebook_last_error"] = str(error)
        except Exception as error:
            update_fields["facebook_last_error"] = f"Unerwarteter Facebook-Fehler: {error}"

    if specific_page.publish_to_instagram and not specific_page.instagram_media_id:
        update_fields["instagram_last_error"] = ""

        try:
            update_fields["instagram_media_id"] = publish_page_to_instagram(specific_page, request)
        except InstagramPublishError as error:
            update_fields["instagram_last_error"] = str(error)
        except Exception as error:
            update_fields["instagram_last_error"] = f"Unerwarteter Instagram-Fehler: {error}"

    if not update_fields:
        return

    BaseContentPage.objects.filter(pk=specific_page.pk).update(**update_fields)
