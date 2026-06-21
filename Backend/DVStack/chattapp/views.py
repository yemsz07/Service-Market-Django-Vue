# chattapp/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .mongodb_services import db # Gamitin ang dot para sa relative import

@login_required 
def get_chat_history(request, room_name):
    if request.method == 'GET':
        # Siguraduhin na ang collection name mo ay 'messages' sa MongoDB Atlas
        messages = db.messages.find({'room_id': room_name}).sort('timestamp', 1)
        
        chat_data = []
        for msg in messages:
            chat_data.append({
                'sender_id': str(msg.get('sender_id')),
                'receiver_id': str(msg.get('receiver_id')),
                'text': msg.get('text'),
                # Siguraduhin na ang timestamp sa MongoDB ay isang datetime object
                'timestamp': msg.get('timestamp').strftime('%Y-%m-%d %H:%M:%S') 
            })
            
        return JsonResponse({'history': chat_data}, status=200)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

#from django.http import JsonResponse

#def get_chat_history(request, room_name):
    #return JsonResponse({'message': 'Success'})
