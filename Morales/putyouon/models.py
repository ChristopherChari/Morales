from django.db import models

# Create your models here.

class Song(models.Model):
    song_id = models.CharField(max_length=50)
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    cover_url = models.CharField(max_length=200)

