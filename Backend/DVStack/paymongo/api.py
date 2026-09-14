from ninja import Router
from ninja.errors import HttpError
from .schemas import CheckoutRequestSchema, CheckoutResponseSchema
from .paymongo import PayMongoService
from .security import CustomJWTAuth 

router = Router(tags=["PayMongo Payments"], auth=CustomJWTAuth())

@router.post("/checkout/", response=CheckoutResponseSchema)
def create_checkout(request, payload: CheckoutRequestSchema):
   
    current_user = request.user 
    
    paymongo = PayMongoService()
    
    success_url = "http://localhost:5173/payment-success"
    cancel_url = "http://localhost:5173/payment-cancelled"

    status_code, response_data = paymongo.create_checkout_session(
        amount=payload.amount,
        description=f"Payment by {current_user.username} - {payload.description}",
        success_url=success_url,
        cancel_url=cancel_url
    )

    if status_code in [200, 201]:
        checkout_url = response_data['data']['attributes']['checkout_url']
        return {"checkout_url": checkout_url}
    
    error_detail = response_data.get("errors", [{}])[0].get("detail", "Payment initialization failed.")
    raise HttpError(status_code if status_code >= 400 else 400, error_detail)