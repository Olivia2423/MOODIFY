from django.shortcuts import render
from .models import Product

def mood_shop_widget(request, mood_key: str):
    qs = Product.objects.all()
    filtered = [p for p in qs if mood_key in (p.mood_keys or p.tags)]
    return render(request, "components/shop_widget.html", {"products": filtered[:6]})
