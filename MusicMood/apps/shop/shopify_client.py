import httpx
from django.conf import settings

def base_url():
    shop = settings.SHOPIFY["SHOP"]
    return f"https://{shop}/admin/api/2024-10"

HEADERS = lambda: {
    "X-Shopify-Access-Token": settings.SHOPIFY["ACCESS_TOKEN"],
    "Content-Type": "application/json",
}

async def list_products(session: httpx.AsyncClient, updated_at_min: str | None = None):
    params = {"limit": 250}
    if updated_at_min:
        params["updated_at_min"] = updated_at_min
    r = await session.get(f"{base_url()}/products.json", params=params, headers=HEADERS())
    r.raise_for_status()
    return r.json()["products"]
