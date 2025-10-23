from django.db import migrations


class Migration(migrations.Migration):
    # Make this migration a no-op by depending on 0006 which already creates the table
    dependencies = [
        ('complaints', '0006_adminaccessaudit'),
    ]

    operations = []
