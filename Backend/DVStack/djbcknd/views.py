# File: djbcknd/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Service
from .serializers import ProductSerializer, ServiceSerializer   

@api_view(['GET'])
def service_list(request):
    try:
        service = Service.objects.all()
        serializer = ServiceSerializer(service, many=True)
        return Response(serializer.data)
    except Service.DoesNotExist:
        return Response({"error": "Service not found"}, status=404)


@api_view(['GET'])
def buyandsell_list(request):
    try:
        product = Product.objects.all()
        serializer = ProductSerializer(product, many=True)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

