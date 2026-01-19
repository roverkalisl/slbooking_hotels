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

# Add hotel, edit hotel, add room, add manual booking (කලින් තියෙන code එක keep කරන්න)

# Static pages (about, privacy_policy, terms_of_service, refund_policy, cancellation_policy, contact, services)

# ads.txt
def ads_txt(request):
    content = "google.com, pub-7289676285085159, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")