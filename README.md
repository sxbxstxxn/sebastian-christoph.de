# sebastian-christoph.de – Wagtail-Neustart

Erste Version für einen privaten Blog mit Django + Wagtail.

## Enthaltene Inhaltsstruktur

- Allgemeiner Blogbeitrag
- Reisen
- Filme & Serien
- Spiele
- Bücher
- Kochen
- Sonstiges

## Lokal starten

```bash
cp .env.example .env
docker compose up --build
```

In einem zweiten Terminal:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Danach:

- Website: http://localhost:8000/
- Admin: http://localhost:8000/admin/

## Facebook-Veröffentlichung

Blogbeiträge können beim Veröffentlichen automatisch als Link-Post auf einer Facebook-Seite veröffentlicht werden. Dafür im Wagtail-Admin beim Beitrag `Auf Facebook veröffentlichen` aktivieren.

Benötigte Umgebungsvariablen:

```env
PUBLIC_SITE_URL=https://sebastian-christoph.de
FACEBOOK_PAGE_ID=...
FACEBOOK_PAGE_ACCESS_TOKEN=...
FACEBOOK_GRAPH_VERSION=v24.0
INSTAGRAM_USER_ID=...
INSTAGRAM_ACCESS_TOKEN=...
```

`FACEBOOK_PAGE_ACCESS_TOKEN` und `INSTAGRAM_ACCESS_TOKEN` sind geheim und dürfen nicht ins Repository.

## Nächste sinnvolle Schritte

1. Startseite und Menü im Wagtail-Admin anlegen.
2. Kategorien/Seitentypen testen.
3. Design verfeinern.
4. Import-/Migrationsstrategie für alte TYPO3-Inhalte planen.
5. Deployment vorbereiten.
