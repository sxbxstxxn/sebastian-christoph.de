from django.core.management.base import BaseCommand
from wagtail.models import Page, Site
from django.utils import timezone

from content.models import (
    HomePage,
    SectionIndexPage,
    BaseContentPage,
    BlogPage,
    TravelPage,
    MovieSeriesPage,
    GamePage,
    BookPage,
    RecipePage,
    MiscPage,
)


class Command(BaseCommand):
    help = "Erstellt Demo-Inhalte für die Website."

    def handle(self, *args, **options):
        root = Page.get_first_root_node()

        # Vorhandene HomePage verwenden oder neu erstellen
        home = HomePage.objects.filter(slug="home").first()

        if not home:
            old_home = Page.objects.child_of(root).filter(slug="home").first()
            if old_home:
                old_home.delete()

            home = HomePage(
                title="Sebastian Christoph",
                slug="home",
                intro="Reisen, Filme & Serien, Spiele, Bücher, Kochen und persönliche Erlebnisse.",
            )
            root.add_child(instance=home)
            home.save_revision().publish()

        Site.objects.update_or_create(
            hostname="localhost",
            port=8000,
            defaults={
                "root_page": home,
                "site_name": "Sebastian Christoph",
                "is_default_site": True,
            },
        )

        sections = [
            ("Reisen", "reisen", "Reiseberichte und persönliche Eindrücke unterwegs."),
            ("Filme & Serien", "filme-serien", "Rezensionen zu Kino, Streaming, Filmen und Serien."),
            ("Spiele", "spiele", "Berichte über PC-Spiele, vor allem von Steam."),
            ("Bücher", "buecher", "Kurze Urteile über Bücher, besonders Fantasy."),
            ("Kochen", "kochen", "Rezepte und Ideen, oft mit dem Thermomix umgesetzt."),
            ("Sonstiges", "sonstiges", "Alles, was sonst noch erlebt werden will."),
        ]

        for title, slug, intro in sections:
            section = SectionIndexPage.objects.child_of(home).filter(slug=slug).first()
            if not section:
                section = SectionIndexPage(title=title, slug=slug, intro=intro)
                home.add_child(instance=section)
                section.save_revision().publish()

        static_pages = [
            (
                "Über mich",
                "ueber-mich",
                "Ein paar Worte über mich und diese Website.",
            ),
            (
                "Kontakt",
                "kontakt",
                "Du möchtest mir schreiben? Dann nutze später das Kontaktformular oder die hinterlegte E-Mail-Adresse.",
            ),
            (
                "Impressum",
                "impressum",
                "Platzhalter für das Impressum. Bitte vor Veröffentlichung mit deinen echten Angaben ersetzen.",
            ),
        ]

        for title, slug, intro in static_pages:
            page = BaseContentPage.objects.child_of(home).filter(slug=slug).first()
            if not page:
                page = BaseContentPage(
                    title=title,
                    slug=slug,
                    date=timezone.now().date(),
                    body=[
                        ("paragraph", intro),
                    ],
                )
                home.add_child(instance=page)
                page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS("Demo-Grundstruktur wurde erstellt."))