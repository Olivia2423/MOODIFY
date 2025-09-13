from django.db import models

class Product(models.Model):
    shopify_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    handle = models.SlugField(max_length=255)
    product_type = models.CharField(max_length=120, blank=True)
    tags = models.JSONField(default=list, blank=True)
    image = models.URLField(blank=True)
    url = models.URLField(blank=True)
    mood_keys = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField()
    def __str__(self):
        return self.title
