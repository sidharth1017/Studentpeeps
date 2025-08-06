from django.urls import path
from . import views
from .Views import bulkUploadView

urlpatterns = [
    path('admin/bulk-upload/', bulkUploadView.BulkUploadView.as_view(), name='bulk_upload'),

    path('<slug:brand_slug>/<slug:offer_custom_id>/', views.OfferPageView.as_view(), name='offer_page'),
    path('<slug:brand_slug>/<slug:offer_custom_id>/get-code/', views.GetCodeView.as_view(), name='get_code'),
]
