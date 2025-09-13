from django.urls import path
from .views import mood_shop_widget
urlpatterns = [path("widget/<slug:mood_key>/", mood_shop_widget, name="mood_shop_widget")]
