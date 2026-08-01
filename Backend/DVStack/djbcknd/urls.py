from django.urls import path, include
from rest_framework.routers import DefaultRouter

# 1. Authenticaton (views/authentication.py)
from .views.authentication import (
    register, 
    login, 
    check_auth, 
    logout
)

# 2. Products & Dashboard Views (views/pdashboard_views.py & product_and_services.py)
from .views.pdashboard_views import (
    ProductViewSet, 
    portal_dashboard, 
    get_items_for_sale
)
from .views.product_and_services import (
    buyandsell_list
)

# 3. Services (views/service_views.py & product_and_services.py)
from .views.service_views import (
    CategoryListView, 
    create_service,
)
from .views.product_and_services import (
    service_list
)

# 4. Providers (views/apply_provider.py)
from .views.apply_provider import (
    apply_as_provider, 
    check_provider_status
)

# 5. Inquiries (views/inquiry_views.py)
from .views.inquiry_views import (
    create_inquiry, 
    get_inquiries
)

# Router Setup para sa ViewSets
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

# URL Patterns
urlpatterns = [
    # 🔑 AUTHENTICATION ENDPOINTS
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('check-auth/', check_auth, name='check-auth'),
    path('logout/', logout, name='logout'),

    # 🛒 PRODUCTS & MARKETPLACE ENDPOINTS
    path('buyandsell/', buyandsell_list, name='buyandsell-list'),
    path('portal-dashboard/', portal_dashboard, name='portal-dashboard'),
    path('get-items-for-sale/', get_items_for_sale, name='get-items-for-sale'),

    # 🛠️ SERVICES & CATEGORIES ENDPOINTS
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('create-service/', create_service, name='create-service'),
    path('services/', service_list, name='service-list'),

    # 🧑‍🔧 PROVIDER VERIFICATION ENDPOINTS
    path('apply-as-provider/', apply_as_provider, name='apply-as-provider'),
    path('check-provider-status/', check_provider_status, name='check-provider-status'),

    # 📩 INQUIRIES ENDPOINTS
    path('create-inquiry/', create_inquiry, name='create-inquiry'),
    path('get-inquiries/', get_inquiries, name='get-inquiries'),

    # 📦 ROUTER URLS (ProductViewSet)
    path('', include(router.urls)),
]