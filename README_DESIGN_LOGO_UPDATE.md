# Design- und Logo-Update

Dieses Update ersetzt die starke beige/warme Gestaltung durch eine schlichtere, hellere Optik, die näher an der aktuellen Ursprungsversion liegt: weißer Hintergrund, klare schwarze/graue Typografie, dezente Linien, einfache Navigation.

## Einspielen

Den Inhalt dieses ZIPs in den Projektordner kopieren:

```text
C:\webprojects\myblog\sebastian_blog_wagtail_start\sebastian_blog\
```

Danach die Container neu starten:

```bash
docker compose down
docker compose up -d --build
```

## Logo

Lege das Logo der alten Seite hier ab:

```text
content/static/images/logo.png
```

Falls dein Logo SVG ist, entweder als `logo.png` exportieren oder in `content/templates/content/base.html` den Dateinamen von `logo.png` auf `logo.svg` ändern.

Wenn keine Logo-Datei vorhanden ist, zeigt die Seite automatisch den Text „Sebastians Blog“.
