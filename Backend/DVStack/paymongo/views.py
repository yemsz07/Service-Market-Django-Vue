from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .paymongo import PayMongoService

class CreateCheckoutView(APIView):
    def post(self, request):
        amount = request.data.get('amount')
        description = request.data.get('description', 'Service Payment')

        # Simple validation
        if not amount:
            return Response({'error': 'Amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        paymongo = PayMongoService()
        
        # Redirection URLs para sa Vue application mo
        success_url = "http://localhost:5173/payment-success"
        cancel_url = "http://localhost:5173/payment-cancelled"

        status_code, response_data = paymongo.create_checkout_session(
            amount=amount,
            description=description,
            success_url=success_url,
            cancel_url=cancel_url
        )

        if status_code in [200, 201]:
            # Makukuha rito ang link kung saan magbabayad si customer
            checkout_url = response_data['data']['attributes']['checkout_url']
            return Response({'checkout_url': checkout_url}, status=status.HTTP_200_OK)

        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)