import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.images import get_image_model
from django.core.files.images import ImageFile

from content.models import (
    SectionIndexPage,
    TravelPage,
    MovieSeriesPage,
    GamePage,
    BookPage,
    RecipePage,
    BlogPage,
)

BASE_URL = "https://sebastian-christoph.de"

CATEGORY_MAP = {
    "reisen": (TravelPage, "reisen"),
    "filme-serien": (MovieSeriesPage, "filme-serien"),
    "spiele": (GamePage, "spiele"),
    "buecher": (BookPage, "buecher"),
    "kochen": (RecipePage, "kochen"),
    "sonstiges": (BlogPage, "sonstiges"),
}


class Command(BaseCommand):
    help = "Importiert alte TYPO3-Beiträge inkl. Inhalt und Bildern."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--replace", action="store_true")
        parser.add_argument("--url", type=str)

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        replace = options["replace"]
        single_url = options.get("url")

        if single_url:
            urls_by_category = {
                self.detect_category(single_url): [single_url]
            }
        else:
            urls_by_category = self.collect_urls_by_category()

        for category_slug, urls in urls_by_category.items():
            model_class, target_section_slug = CATEGORY_MAP[category_slug]
            section = SectionIndexPage.objects.filter(slug=target_section_slug).first()

            if not section:
                self.stdout.write(self.style.WARNING(f"Rubrik fehlt: {target_section_slug}"))
                continue

            for url in sorted(urls):
                data = self.parse_article(url)
                if not data:
                    continue

                self.stdout.write(f"{category_slug}: {data['title']}")

                if dry_run:
                    continue

                existing = section.get_children().filter(slug=data["slug"]).first()
                if existing and replace:
                    existing.delete()
                    existing = None

                if existing:
                    self.stdout.write(f"  übersprungen, existiert schon: {data['slug']}")
                    continue

                page = model_class(
                    title=data["title"],
                    slug=data["slug"],
                    date=data["date"],
                    teaser=data["subtitle"],
                    body=data["body"],
                )

                if data.get("main_image"):
                    page.hero_image = data["main_image"]

                section.add_child(instance=page)
                page.save_revision().publish()

        self.stdout.write(self.style.SUCCESS("Import abgeschlossen."))

    def collect_urls_by_category(self):
        result = {key: set() for key in CATEGORY_MAP.keys()}

        for category_slug in result.keys():
            url = f"{BASE_URL}/{category_slug}"
            html = requests.get(url, timeout=20).text
            soup = BeautifulSoup(html, "html.parser")

            for a in soup.find_all("a", href=True):
                href = urljoin(BASE_URL, a["href"])
                parsed = urlparse(href)

                if parsed.netloc.endswith("sebastian-christoph.de") and "/blog/" in parsed.path:
                    result[category_slug].add(href)

        return result
        
    def detect_category(self, url):
        url = url.lower()

        if "reisen" in url:
            return "reisen"

        if any(x in url for x in [
            "jexi",
            "paradise",
            "film",
            "serie"
        ]):
            return "filme-serien"

        if "kochen" in url or "kassler" in url:
            return "kochen"

        return "sonstiges"        

    def parse_article(self, url):
        html = requests.get(url, timeout=20).text
        soup = BeautifulSoup(html, "html.parser")

        h1 = soup.find("h1")
        if not h1:
            return None

        title = h1.get_text(" ", strip=True)
        slug = slugify(urlparse(url).path.rstrip("/").split("/")[-1])

        h2 = h1.find_next("h2")
        subtitle = h2.get_text(" ", strip=True) if h2 else ""

        text = soup.get_text("\n", strip=True)
        date_match = re.search(r"erstellt am (\d{2})\.(\d{2})\.(\d{4})", text)
        if date_match:
            day, month, year = date_match.groups()
            date = f"{year}-{month}-{day}"
        else:
            date = "2024-01-01"

        body = []
        main_image = None

        current = h1
        while current:
            current = current.find_next()

            if not current:
                break

            if current.name == "footer":
                break

            txt = current.get_text(" ", strip=True)

            if txt.startswith("©"):
                break

            if current.name in ["nav", "script", "style"]:
                continue

            if current.name == "h1":
                continue

            if current.name == "h2":
                continue

            if txt.startswith("erstellt am"):
                continue

            if current.name in ["h3", "h4", "h5"]:
                if txt and not txt.lower().startswith("rating"):
                    body.append(("heading", txt))
                continue

            if current.name == "p":
                if txt and not self.is_social_text(txt):
                    body.append(("paragraph", txt))
                continue

            if current.name == "img":
                image = self.import_image(current, url)
                if image:
                    if not main_image:
                        main_image = image
                    body.append(("image", image))
                continue

        if not body and subtitle:
            body.append(("paragraph", subtitle))

        return {
            "title": title,
            "slug": slug,
            "subtitle": subtitle,
            "date": date,
            "body": body,
            "main_image": main_image,
        }

    def import_image(self, img, page_url):
        src = img.get("src") or img.get("data-src")
        if not src:
            return None

        image_url = urljoin(page_url, src)

        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
        except Exception:
            return None

        filename = image_url.split("/")[-1].split("?")[0] or "imported-image.jpg"

        Image = get_image_model()
        existing = Image.objects.filter(title=filename).first()
        if existing:
            return existing

        image = Image(title=filename)
        image.file = ImageFile(ContentFile(response.content), name=filename)
        image.save()
        return image

    def is_social_text(self, txt):
        bad = ["twitter.com", "facebook.com", "instagram.com", "kontakt", "impressum"]
        return any(x in txt.lower() for x in bad)