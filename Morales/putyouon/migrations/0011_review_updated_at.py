# Generated by Django 4.2.5 on 2023-09-09 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('putyouon', '0010_review_edited'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
