from django.urls import path
from .views import service_list, buyandsell_list

urlpatterns = [
    # Ito 'yung mismong endpoint natin
    path('services/', service_list, name='service-list'),
    path('buyandsell/', buyandsell_list, name='buyandsell-list'),
]