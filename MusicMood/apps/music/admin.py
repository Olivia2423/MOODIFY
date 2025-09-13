from django.contrib import admin
from .models import Mood, Artist, Track, PlayEvent
admin.site.register(Mood)
admin.site.register(Artist)
admin.site.register(Track)
admin.site.register(PlayEvent)
