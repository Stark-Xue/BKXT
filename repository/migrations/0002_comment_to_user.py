# Generated by Django 3.0.4 on 2020-07-31 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='to_user',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
