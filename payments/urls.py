from django.urls import path
from .views import CheckoutMpesaView

urlpatterns = [
    # path('payment', views.checkout_mpesa, name='checkout_mpesa'),
    path('payment/', CheckoutMpesaView.as_view(), name='checkout_mpesa'),
]
