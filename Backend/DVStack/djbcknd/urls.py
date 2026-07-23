from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    service_list, 
    buyandsell_list, 
    login, 
    register, 
    check_auth, 
    logout, 
    portal_dashboard, 
    get_items_for_sale,
    ProductViewSet
)

# 2. Gumawa ng DefaultRouter instance
router = DefaultRouter()

# 3. I-register ang ProductViewSet para sa automatic CRUD (/api/products/)
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [

    path('services/', service_list, name='service-list'),
    path('buyandsell/', buyandsell_list, name='buyandsell-list'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('check-auth/', check_auth, name='check-auth'),
    path('logout/', logout, name='logout'),
    path('portal-dashboard/', portal_dashboard, name='portal-dashboard'),
    path('get-items-for-sale/', get_items_for_sale, name='get-items-for-sale'),

    # 4. Isama ang router.urls para sa automatic GET, POST, PUT, DELETE ng Products
    path('', include(router.urls)),
]