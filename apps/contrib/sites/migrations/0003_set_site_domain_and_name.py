from django.conf import settings
from django.db import migrations


def _update_or_create_site_with_sequence(site_model, connection, domain, name):
    site, created = site_model.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={
            "domain": domain,
            "name": name,
        },
    )
    if created:
        max_id = site_model.objects.order_by("-id").first().id
        with connection.cursor() as cursor:
            cursor.execute("SELECT last_value from django_site_id_seq")
            (current_id,) = cursor.fetchone()
            if current_id <= max_id:
                cursor.execute(
                    "alter sequence django_site_id_seq restart with %s",
                    [max_id + 1],
                )


def update_site_forward(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    _update_or_create_site_with_sequence(
        Site,
        schema_editor.connection,
        "agentsphere.serveo.net",
        "AgentSphere",
    )


def update_site_backward(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    _update_or_create_site_with_sequence(
        Site,
        schema_editor.connection,
        "example.com",
        "example.com",
    )


class Migration(migrations.Migration):

    dependencies = [("sites", "0002_alter_domain_unique")]

    operations = [migrations.RunPython(update_site_forward, update_site_backward)]
