from django.conf import settings
from django.db import models

class Mood(models.Model):
    key = models.SlugField(unique=True)  # e.g., "chill", "happy", "focus"
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    def __str__(self):
        return self.name

class Track(models.Model):
    title = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    genres = models.JSONField(default=list, blank=True)
    mood_tags = models.ManyToManyField(Mood, related_name="tracks", blank=True)
    duration_sec = models.PositiveIntegerField(default=0)
    preview_url = models.URLField(blank=True)  # audio preview
    vector = models.JSONField(null=True, blank=True)  # embedding vector

class PlayEvent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    mood = models.ForeignKey(Mood, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.BooleanField(default=False)
