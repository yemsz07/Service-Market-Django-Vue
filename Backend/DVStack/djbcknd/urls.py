from django.urls import path
from .views import service_list, buyandsell_list, login, register, check_auth, logout

urlpatterns = [
    # Ito 'yung mismong endpoint natin
    path('services/', service_list, name='service-list'),
    path('buyandsell/', buyandsell_list, name='buyandsell-list'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('check-auth/', check_auth, name='check-auth'),
    path('logout/', logout, name='logout'),
]