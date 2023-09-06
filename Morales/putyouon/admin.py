from django.contrib import admin
from .models import Song
from .models import Like

# Register your models here.

admin.site.register(Like)
admin.site.register(Song)
