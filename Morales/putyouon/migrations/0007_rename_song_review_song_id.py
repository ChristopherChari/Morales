# Generated by Django 4.2.5 on 2023-09-09 15:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('putyouon', '0006_rename_song_id_review_song'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='song',
            new_name='song_id',
        ),
    ]
