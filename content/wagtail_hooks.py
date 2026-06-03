from wagtail import hooks

from .models import BaseContentPage
from .social import FacebookPublishError, publish_page_to_facebook


@hooks.register("after_publish_page")
def publish_to_facebook_after_publish(request, page):
    specific_page = page.specific

    if not isinstance(specific_page, BaseContentPage):
        return

    if not specific_page.publish_to_facebook or specific_page.facebook_post_id:
        return

    update_fields = {"facebook_last_error": ""}

    try:
        update_fields["facebook_post_id"] = publish_page_to_facebook(specific_page, request)
    except FacebookPublishError as error:
        update_fields["facebook_last_error"] = str(error)
    except Exception as error:
        update_fields["facebook_last_error"] = f"Unerwarteter Facebook-Fehler: {error}"

    BaseContentPage.objects.filter(pk=specific_page.pk).update(**update_fields)
