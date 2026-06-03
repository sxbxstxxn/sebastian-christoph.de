from wagtail import hooks

from .models import BaseContentPage
from .social import (
    FacebookPublishError,
    InstagramPublishError,
    publish_page_to_facebook,
    publish_page_to_instagram,
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
