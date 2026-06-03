from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from wagtail.search import index
from wagtail.embeds.blocks import EmbedBlock


class ContentTag(TaggedItemBase):
    content_object = ParentalKey(
        "BaseContentPage",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class HomePage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]

    subpage_types = ["content.SectionIndexPage", "content.BaseContentPage"]

    def get_context(self, request):
        context = super().get_context(request)
        context["latest_posts"] = BaseContentPage.objects.live().public().order_by("-date")[:6]
        return context


class SectionIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = [
        "content.BlogPage",
        "content.TravelPage",
        "content.MovieSeriesPage",
        "content.GamePage",
        "content.BookPage",
        "content.RecipePage",
        "content.MiscPage",
    ]

    def get_context(self, request):
        context = super().get_context(request)
        posts = self.get_children().live().specific()
        context["posts"] = sorted(
            posts,
            key=lambda page: getattr(page, "date", page.first_published_at),
            reverse=True,
        )
        return context


class BaseContentPage(Page):
    date = models.DateField("Datum")
    teaser = models.TextField("Kurzbeschreibung", blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Titelbild",
    )
    publish_to_facebook = models.BooleanField("Auf Facebook veröffentlichen", default=False)
    facebook_post_id = models.CharField("Facebook Post-ID", max_length=255, blank=True, editable=False)
    facebook_last_error = models.TextField("Letzter Facebook-Fehler", blank=True, editable=False)
    publish_to_instagram = models.BooleanField("Auf Instagram veröffentlichen", default=False)
    instagram_media_id = models.CharField("Instagram Media-ID", max_length=255, blank=True, editable=False)
    instagram_last_error = models.TextField("Letzter Instagram-Fehler", blank=True, editable=False)
    
    body = StreamField([
        ("heading", blocks.CharBlock(
            label="Überschrift",
            icon="title",
        )),
        ("paragraph", blocks.RichTextBlock(
            label="Text",
            icon="pilcrow",
        )),

        ("sized_image", blocks.StructBlock([
            ("image", ImageChooserBlock(label="Bild")),
            ("size", blocks.ChoiceBlock(
                choices=[
                    ("full", "Volle Breite"),
                    ("medium", "2/3 Breite"),
                    ("small", "1/3 Breite zentriert"),
                ],
                default="full",
                label="Darstellung",
            )),
        ],
            icon="image",
            label="Einzelbild",
        )),        
        ("embed", EmbedBlock(
            label="YouTube / Video",
            icon="media",
        )),
        ("gallery", blocks.StructBlock([
            ("columns", blocks.ChoiceBlock(
                choices=[
                    ("2", "2 Spalten"),
                    ("3", "3 Spalten"),
                ],
                default="3",
                label="Spalten",
            )),
            ("images", blocks.ListBlock(
                ImageChooserBlock(),
                label="Bilder",
            )),
        ],
            template="content/blocks/gallery.html",
            label="Bildergalerie",
            icon="image",
        )),
    ], use_json_field=True, blank=True)

    tags = ClusterTaggableManager(through=ContentTag, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("teaser"),
        index.SearchField("body"),
        index.RelatedFields("tags", [index.SearchField("name")]),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("date"),
            FieldPanel("teaser"),
            FieldPanel("hero_image"),
            FieldPanel("tags"),
        ], heading="Metadaten"),
        MultiFieldPanel([
            FieldPanel("publish_to_facebook"),
            FieldPanel("facebook_post_id", read_only=True),
            FieldPanel("facebook_last_error", read_only=True),
            FieldPanel("publish_to_instagram"),
            FieldPanel("instagram_media_id", read_only=True),
            FieldPanel("instagram_last_error", read_only=True),
        ], heading="Social Media"),
        FieldPanel("body"),
    ]

    class Meta:
        abstract = False
        verbose_name = "Allgemeiner Blogbeitrag"


class BlogPage(BaseContentPage):
    parent_page_types = ["content.SectionIndexPage", "content.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = "Allgemeiner Blogbeitrag"


class TravelPage(BaseContentPage):
    destination = models.CharField("Reiseziel", max_length=255, blank=True)
    travel_date = models.CharField("Reisezeitraum", max_length=255, blank=True)

    content_panels = BaseContentPage.content_panels + [
        MultiFieldPanel([
            FieldPanel("destination"),
            FieldPanel("travel_date"),
        ], heading="Reisedaten")
    ]

    class Meta:
        verbose_name = "Reisen"


class MovieSeriesPage(BaseContentPage):
    provider = models.CharField(
        "Streaminganbieter/Kino",
        max_length=50,
        blank=True,
        choices=[
            ("netflix", "Netflix"),
            ("amazon-prime-video", "Amazon Prime Video"),
            ("disney-plus", "Disney+"),
            ("apple-tv-plus", "Apple TV+"),
            ("wow", "WOW"),
            ("paramount-plus", "Paramount+"),
            ("kino", "Kino"),
            ("mediathek", "Mediathek"),
            ("blu-ray-dvd", "Blu-ray / DVD"),
            ("sonstiges", "Sonstiges"),
        ],
)
    rating = models.PositiveSmallIntegerField(
        "Bewertung",
        choices=[
            (1, "★☆☆☆☆"),
            (2, "★★☆☆☆"),
            (3, "★★★☆☆"),
            (4, "★★★★☆"),
            (5, "★★★★★"),
        ],
        null=True,
        blank=True,
    )

    content_panels = BaseContentPage.content_panels + [
        MultiFieldPanel([
            FieldPanel("provider"),
            FieldPanel("rating"),
        ], heading="Film-/Seriendaten")
    ]

    class Meta:
        verbose_name = "Filme & Serien"


class GamePage(BaseContentPage):
    platform = models.CharField("Plattform", max_length=255, default="PC / Steam")
    steam_url = models.URLField("Steam-Link", blank=True)
    rating = models.PositiveSmallIntegerField("Bewertung 1–10", null=True, blank=True)

    content_panels = BaseContentPage.content_panels + [
        MultiFieldPanel([
            FieldPanel("platform"),
            FieldPanel("steam_url"),
            FieldPanel("rating"),
        ], heading="Spieldaten")
    ]

    class Meta:
        verbose_name = "Spiele"


class BookPage(BaseContentPage):
    author = models.CharField("Autor/in", max_length=255, blank=True)
    genre = models.CharField("Genre", max_length=255, default="Fantasy", blank=True)
    rating = models.PositiveSmallIntegerField("Bewertung 1–10", null=True, blank=True)

    content_panels = BaseContentPage.content_panels + [
        MultiFieldPanel([
            FieldPanel("author"),
            FieldPanel("genre"),
            FieldPanel("rating"),
        ], heading="Buchdaten")
    ]

    class Meta:
        verbose_name = "Bücher"


class RecipePage(BaseContentPage):
    servings = models.PositiveSmallIntegerField("Portionen", null=True, blank=True)
    duration = models.CharField("Dauer", max_length=100, blank=True)
    thermomix = models.BooleanField("Thermomix-Rezept", default=True)
    ingredients = RichTextField("Zutaten", blank=True)

    content_panels = BaseContentPage.content_panels + [
        MultiFieldPanel([
            FieldPanel("servings"),
            FieldPanel("duration"),
            FieldPanel("thermomix"),
            FieldPanel("ingredients"),
        ], heading="Rezeptdaten")
    ]

    class Meta:
        verbose_name = "Kochen"


class MiscPage(BaseContentPage):
    class Meta:
        verbose_name = "Sonstiges"
