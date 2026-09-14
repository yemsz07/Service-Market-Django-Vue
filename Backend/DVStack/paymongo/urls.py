from django.urls import path
from .views import CreateCheckoutView

urlpatterns = [
    path('checkout/', CreateCheckoutView.as_view(), name='paymongo-checkout'),
]