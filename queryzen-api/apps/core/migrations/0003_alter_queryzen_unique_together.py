# Generated by Django 5.1.5 on 2025-01-29 18:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_execution_zen'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='queryzen',
            unique_together={('collection', 'name', 'version')},
        ),
    ]
