# context_processors.py
from .models import Offer, Category
from django.db.models import Count

def search_offers(request):
    offers = Offer.objects.all().order_by('-sorting')
    brand_offer_counts = (
        Offer.objects.values('brand')
        .annotate(total=Count('id'))
    )
    brand_offer_map = {item['brand']: item['total'] for item in brand_offer_counts}

    offers_with_links = []
    for offer in offers:
        if brand_offer_map.get(offer.brand.id, 0) > 1:
            link = f"/brand/{offer.brand.slug}/"
        else:
            link = f"/offer/{offer.brand.slug}/{offer.custom_id}/"
        offer.link = link

    return {'search_offers': offers}

def categories(request):
    categories = Category.objects.filter(isVisible=True).order_by('-sorting')
    return {'categories': categories}
 