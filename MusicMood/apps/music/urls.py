from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("_recs/", views.htmx_recs, name="htmx_recs_qs"),
    path("_recs/<slug:mood_key>/", views.htmx_recs, name="htmx_recs"),
    path("api/recs/", views.api_recs, name="api_recs"),
]
