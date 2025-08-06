# context_processors.py
from .models import Offer, Category

def search_offers(request):
    offers = Offer.objects.all().order_by('-sorting')
    return {'search_offers': offers}

def categories(request):
    categories = Category.objects.filter(isVisible=True).order_by('-sorting')
    return {'categories': categories}
