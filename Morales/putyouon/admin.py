from django.contrib import admin
from .models import Song
from .models import Like
from .models import Review

# Register your models here.


admin.site.register(Review)
admin.site.register(Like)
admin.site.register(Song)
