from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Booking, Hotel
from .serializers import BookingSerializer, HotelSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_bookings_api(request):
    if request.user.profile.role != 'owner':
        return Response({"error": "Access denied"}, status=403)
    bookings = Booking.objects.filter(hotel__owner=request.user)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def owner_hotels_api(request):
    if request.user.profile.role != 'owner':
        return Response({"error": "Access denied"}, status=403)
    hotels = Hotel.objects.filter(owner=request.user)
    serializer = HotelSerializer(hotels, many=True)
    return Response(serializer.data)