from celery import shared_task
import httpx
from django.utils import timezone
from django.conf import settings
from .models import Product
from .shopify_client import list_products

@shared_task
def sync_shopify_products():
    async def run():
        async with httpx.AsyncClient(timeout=30) as s:
            items = await list_products(s)
        for p in items:
            Product.objects.update_or_create(
                shopify_id=str(p["id"]),
                defaults={
                    "title": p["title"],
                    "handle": p["handle"],
                    "product_type": p.get("product_type", ""),
                    "tags": p.get("tags", "").split(",") if p.get("tags") else [],
                    "image": (p.get("image") or {}).get("src", ""),
                    "url": f"https://{settings.SHOPIFY['SHOP']}/products/{p['handle']}",
                    "updated_at": timezone.now(),
                },
            )
    import anyio
    anyio.run(run)
