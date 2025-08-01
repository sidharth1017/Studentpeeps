# context_processors.py
from .models import Offer

def search_offers(request):
    offers = Offer.objects.all().order_by('-sorting')
    return {'search_offers': offers}

