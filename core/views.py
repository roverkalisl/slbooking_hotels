from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import hashlib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Booking, Hotel
from .serializers import BookingSerializer, HotelSerializer  # serializers.py එක තියෙනවා නම්
from .models import Hotel, Room, Booking, Profile, SiteStats
from .forms import HotelForm, RoomForm, ManualBookingForm, CustomUserCreationForm


# Home page with global view count
@never_cache
def home(request):
    hotels = Hotel.objects.all()[:6]
    
    # Global view count
    stats, created = SiteStats.objects.get_or_create(pk=1, defaults={'total_views': 0})
    stats.total_views += 1
    stats.save()
    
    return render(request, 'core/home.html', {
        'hotels': hotels,
        'total_views': stats.total_views
    })

# Register with custom form
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to SL Booking Hotels.')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# Search hotels
def search_hotels(request):
    query = request.GET.get('q', '')
    hotels = Hotel.objects.all()
    if query:
        hotels = hotels.filter(Q(name__icontains=query) | Q(address__icontains=query))
    return render(request, 'core/search.html', {'hotels': hotels, 'query': query})

# Hotel detail
def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    return render(request, 'core/hotel_detail.html', {'hotel': hotel})

# Book room
@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        check_in = request.POST['check_in']
        check_out = request.POST['check_out']
        Booking.objects.create(
            hotel=room.hotel,
            room=room,
            user=request.user,
            check_in=check_in,
            check_out=check_out
        )
        messages.success(request, 'Booking request sent! Waiting for confirmation.')
        return redirect('my_bookings')
    return render(request, 'core/book_room.html', {'room': room})

# Book villa
@login_required
def book_villa(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        check_in = request.POST['check_in']
        check_out = request.POST['check_out']
        Booking.objects.create(
            hotel=hotel,
            user=request.user,
            check_in=check_in,
            check_out=check_out
        )
        messages.success(request, 'Booking request sent! Waiting for confirmation.')
        return redirect('my_bookings')
    return render(request, 'core/book_villa.html', {'hotel': hotel})

# My bookings
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')
    return render(request, 'core/my_bookings.html', {'bookings': bookings})

# Cancel booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, 'Booking cancelled.')
    return redirect('my_bookings')

# Owner dashboard
@login_required
def owner_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    hotels = Hotel.objects.filter(owner=request.user)
    pending_bookings = Booking.objects.filter(hotel__owner=request.user, status='pending').count()
    return render(request, 'core/owner_dashboard.html', {
        'hotels': hotels,
        'pending_bookings': pending_bookings
    })

# Manager dashboard
@login_required
def manager_dashboard(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'manager':
        messages.error(request, 'Access denied. Only managers can view this page.')
        return redirect('home')
    
    all_bookings = Booking.objects.all().order_by('-id')
    pending_bookings = all_bookings.filter(status='pending').count()
    
    return render(request, 'core/manager_dashboard.html', {
        'bookings': all_bookings,
        'pending_bookings': pending_bookings
    })

# Owner bookings
@login_required
def owner_bookings(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    bookings = Booking.objects.filter(hotel__owner=request.user).order_by('-id')
    return render(request, 'core/owner_bookings.html', {'bookings': bookings})

# Confirm booking
@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not hasattr(request.user, 'profile') or (request.user != booking.hotel.owner and request.user.profile.role != 'manager'):
        messages.error(request, 'Access denied.')
        return redirect('owner_bookings')
    
    nights = (booking.check_out - booking.check_in).days
    price = booking.room.price_per_night if booking.room else booking.hotel.price_per_night
    booking.amount = price * nights
    booking.status = 'confirmed'
    booking.save()

    # SMS code (කලින් තියෙන safe version එක keep කරන්න)

    messages.success(request, 'Booking confirmed successfully!')
    return render(request, 'core/booking_success.html')

# Reject booking
@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not hasattr(request.user, 'profile') or (request.user != booking.hotel.owner and request.user.profile.role != 'manager'):
        messages.error(request, 'Access denied.')
        return redirect('owner_bookings')
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, 'Booking rejected.')
    return redirect('manager_dashboard' if request.user.profile.role == 'manager' else 'owner_bookings')

# Add hotel
@login_required
def add_hotel(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'owner':
        messages.error(request, 'Access denied. Only owners can add hotels.')
        return redirect('home')
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.save()
            form.save_m2m()  # for facilities MultiSelectField
            messages.success(request, 'Hotel added successfully!')
            return redirect('owner_dashboard')
    else:
        form = HotelForm()
    return render(request, 'core/add_hotel.html', {'form': form})

# Edit hotel
@login_required
def edit_hotel(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Hotel updated successfully!')
            return redirect('owner_dashboard')
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'core/edit_hotel.html', {'form': form, 'hotel': hotel})

# Add room
@login_required
def add_room(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()
            messages.success(request, 'Room added successfully!')
            return redirect('owner_dashboard')
    else:
        form = RoomForm()
    return render(request, 'core/add_room.html', {'form': form, 'hotel': hotel})

# Add manual booking
@login_required
def add_manual_booking(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == 'POST':
        form = ManualBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.hotel = hotel
            booking.status = 'confirmed'  # manual එක auto confirm
            booking.save()
            messages.success(request, 'Manual booking added successfully!')
            return redirect('owner_bookings')
    else:
        form = ManualBookingForm()
    return render(request, 'core/add_manual_booking.html', {'form': form, 'hotel': hotel})
    
    # Static pages
def about(request):
    return render(request, 'core/about.html')

def services(request):
    return render(request, 'core/services.html')

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

def terms_of_service(request):
    return render(request, 'core/terms_of_service.html')

def refund_policy(request):
    return render(request, 'core/refund_policy.html')

def cancellation_policy(request):
    return render(request, 'core/cancellation_policy.html')

def contact(request):
    if request.method == 'POST':
        # Simple contact form (later email send add කරන්න පුළුවන්)
        messages.success(request, 'Your message has been sent! We will contact you soon.')
        return redirect('contact')
    return render(request, 'core/contact.html')
# Add hotel, edit hotel, add room, add manual booking (කලින් තියෙන code එක keep කරන්න)

# Static pages (about, privacy_policy, terms_of_service, refund_policy, cancellation_policy, contact, services)

# ads.txt
def ads_txt(request):
    content = "google.com, pub-7289676285085159, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")
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