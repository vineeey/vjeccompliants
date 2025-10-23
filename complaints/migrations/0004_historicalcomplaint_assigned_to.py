from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("complaints", "0003_complaint_assigned_to"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalcomplaint",
            name="assigned_to",
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.DO_NOTHING, related_name="+", to=settings.AUTH_USER_MODEL),
        ),
    ]
