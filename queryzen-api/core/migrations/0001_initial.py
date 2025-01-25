# Generated by Django 5.1.5 on 2025-01-25 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LambdaQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('query', models.TextField()),
                ('version', models.TextField()),
            ],
            options={
                'unique_together': {('name', 'version')},
            },
        ),
    ]
