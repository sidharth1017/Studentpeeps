from django.urls import path
from . import views
urlpatterns = [
    path('<slug:sku>/', views.GiftcardPageView.as_view(), name='giftcard_page')
]