from django.urls import path
from . import views

app_name = 'giftcard'

urlpatterns = [
    path('cart/',            views.CartView.as_view(),            name='cart_view'),
    path('cart/add/',        views.AddToCartView.as_view(),        name='add_to_cart'),
    path('cart/remove/',     views.RemoveFromCartView.as_view(),   name='remove_from_cart'),
    path('cart/update/',     views.UpdateCartItemView.as_view(),   name='update_cart_item'),

    # Payment flow (Shared / Razorpay)
    path('payment/initiate/',  views.InitiatePaymentView.as_view(),  name='initiate_payment'),
    path('payment/callback/',  views.PaymentCallbackView.as_view(),  name='payment_callback'),
    
    # Payment flow (PayU specific redirects)
    path('payment/payu/success/', views.PayUSuccessView.as_view(),   name='payu_success'),
    path('payment/payu/failure/', views.PayUFailureView.as_view(),   name='payu_failure'),

    # Post-payment UI
    path('order/<str:reference_id>/success/', views.OrderSuccessView.as_view(), name='order_success'),
    path('order/<str:reference_id>/failed-refund/', views.OrderFailedRefundView.as_view(), name='order_failed_refund'),
    path('order/<str:reference_id>/detail/',  views.OrderDetailView.as_view(),  name='order_detail'),

    # Explore page
    path('explore/',          views.ExploreView.as_view(),        name='explore'),

    # Product page (must be last to avoid consuming other patterns)
    path('<slug:sku>/',       views.GiftcardPageView.as_view(),    name='giftcard_page'),
]