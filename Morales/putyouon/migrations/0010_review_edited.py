# Generated by Django 4.2.5 on 2023-09-09 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('putyouon', '0009_rename_song_review_song_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='edited',
            field=models.BooleanField(default=False),
        ),
    ]