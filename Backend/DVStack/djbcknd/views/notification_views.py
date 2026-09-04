from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from djbcknd.serializers import NotificationSerializer
from djbcknd.models import Notification
from djbcknd.authentication import CustomJWTAuthentication
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """
    Fetch all notifications for the currently authenticated user.
    Ordered by most recent first.
    """
    try:
        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')
        
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            'notifications': serializer.data,
            'unread_count': notifications.filter(is_read=False).count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"[NOTIFICATIONS] Error fetching notifications: {e}")
        return Response({
            'error': 'Failed to fetch notifications'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a specific notification as read.
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        
        return Response({
            'message': 'Notification marked as read'
        }, status=status.HTTP_200_OK)
        
    except Notification.DoesNotExist:
        return Response({
            'error': 'Notification not found'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        print(f"[NOTIFICATIONS] Error marking notification as read: {e}")
        return Response({
            'error': 'Failed to mark notification as read'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([CustomJWTAuthentication])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Mark all notifications for the current user as read.
    """
    try:
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'message': 'All notifications marked as read'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"[NOTIFICATIONS] Error marking all notifications as read: {e}")
        return Response({
            'error': 'Failed to mark all notifications as read'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
