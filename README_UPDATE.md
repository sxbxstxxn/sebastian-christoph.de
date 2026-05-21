# Update: Design und Demo-Inhalte

Dieses Paket ergänzt das bestehende Wagtail-Projekt um:

- überarbeitete Templates
- neues CSS im Stil eines persönlichen Blogs
- Startseite mit Rubriken und Teaserbereich
- Demo-Inhalte für Reisen, Filme & Serien, Spiele, Bücher, Kochen und Sonstiges
- Management-Command `seed_demo_content`

## Installation

Den Inhalt dieses Update-Pakets in deinen bestehenden Projektordner kopieren, also nach:

```text
C:\webprojects\myblog\sebastian_blog_wagtail_start\sebastian_blog\
```

Vorhandene Dateien überschreiben.

Danach im Projektordner ausführen:

```bash
docker compose exec web python manage.py seed_demo_content
```

Falls der Webcontainer nicht läuft:

```bash
docker compose up --build
```

Danach öffnen:

```text
http://localhost:8000/
```
