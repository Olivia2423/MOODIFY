from rest_framework import serializers
from .models import Mood, Track

class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ["key", "name", "description"]

class TrackSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source="artist.name", read_only=True)
    class Meta:
        model = Track
        fields = ["id", "title", "artist_name", "genres", "duration_sec", "preview_url"]
