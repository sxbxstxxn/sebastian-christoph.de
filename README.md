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

## Nächste sinnvolle Schritte

1. Startseite und Menü im Wagtail-Admin anlegen.
2. Kategorien/Seitentypen testen.
3. Design verfeinern.
4. Import-/Migrationsstrategie für alte TYPO3-Inhalte planen.
5. Deployment vorbereiten.
