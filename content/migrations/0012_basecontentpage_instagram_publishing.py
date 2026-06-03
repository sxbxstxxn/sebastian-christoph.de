# Generated manually on 2026-06-03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0011_basecontentpage_facebook_publishing"),
    ]

    operations = [
        migrations.AddField(
            model_name="basecontentpage",
            name="instagram_last_error",
            field=models.TextField(blank=True, editable=False, verbose_name="Letzter Instagram-Fehler"),
        ),
        migrations.AddField(
            model_name="basecontentpage",
            name="instagram_media_id",
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name="Instagram Media-ID"),
        ),
        migrations.AddField(
            model_name="basecontentpage",
            name="publish_to_instagram",
            field=models.BooleanField(default=False, verbose_name="Auf Instagram ver\u00f6ffentlichen"),
        ),
    ]
