# Generated manually on 2026-06-03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0010_alter_basecontentpage_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="basecontentpage",
            name="facebook_last_error",
            field=models.TextField(blank=True, editable=False, verbose_name="Letzter Facebook-Fehler"),
        ),
        migrations.AddField(
            model_name="basecontentpage",
            name="facebook_post_id",
            field=models.CharField(blank=True, editable=False, max_length=255, verbose_name="Facebook Post-ID"),
        ),
        migrations.AddField(
            model_name="basecontentpage",
            name="publish_to_facebook",
            field=models.BooleanField(default=False, verbose_name="Auf Facebook ver\u00f6ffentlichen"),
        ),
    ]
