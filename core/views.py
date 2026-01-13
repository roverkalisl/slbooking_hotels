from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Hotel, Room, Booking, Profile
from .forms import HotelForm, RoomForm, ManualBookingForm
import requests
from django.conf import settings
from django.views.decorators.cache import never_cache

# Home page
@never_cache
def home(request):
    hotels = Hotel.objects.all()[:6]
    
    # Global view count (from SiteStats model)
    from .models import SiteStats
    stats, created = SiteStats.objects.get_or_create(pk=1, defaults={'total_views': 0})
    stats.total_views += 1
    stats.save()
    
    return render(request, 'core/home.html', {
        'hotels': hotels,
        'total_views': stats.total_views
    })

# Register
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user, role='customer')
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

# Login (Django built-in use කරන්න පුළුවන් නම් better)
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
    if request.user.profile.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    hotels = Hotel.objects.filter(owner=request.user)
    pending_bookings = Booking.objects.filter(hotel__owner=request.user, status='pending').count()
    return render(request, 'core/owner_dashboard.html', {
        'hotels': hotels,
        'pending_bookings': pending_bookings
    })

# Add hotel
@login_required
def add_hotel(request):
    if request.user.profile.role != 'owner':
        return redirect('home')
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.save()
            form.save_m2m()
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

# Owner bookings
@login_required
def owner_bookings(request):
    if request.user.profile.role != 'owner':
        return redirect('home')
    bookings = Booking.objects.filter(hotel__owner=request.user).order_by('-id')
    return render(request, 'core/owner_bookings.html', {'bookings': bookings})

# Confirm booking
@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.hotel.owner:
        messages.error(request, 'Access denied.')
        return redirect('owner_bookings')
    
    # Calculate amount
    nights = (booking.check_out - booking.check_in).days
    price = booking.room.price_per_night if booking.room else booking.hotel.price_per_night
    booking.amount = price * nights
    booking.status = 'confirmed'
    booking.save()

    # SMS to Customer
    customer_phone = booking.user.profile.phone_number
    sms_sent_to_customer = False
    if customer_phone:
        try:
            url = "https://textit.biz/sendmsg/index.php"
            payload = {
                "id": settings.TEXTIT_API_ID,
                "pw": settings.TEXTIT_API_PASSWORD,
                "to": customer_phone,
                "text": f"🎉 Your booking at {booking.hotel.name} is CONFIRMED!\nCheck-in: {booking.check_in}\nCheck-out: {booking.check_out}\nTotal: Rs. {booking.amount}\nThank you! - SL Booking Hotels"
            }
            response = requests.get(url, params=payload, timeout=10)
            if response.status_code == 200 and "OK" in response.text:
                sms_sent_to_customer = True
        except Exception as e:
            messages.warning(request, f'Customer SMS failed: {str(e)}')

    # SMS Alert to Owner (safe check)
    sms_sent_to_owner = False
    owner_phone = getattr(settings, 'OWNER_ALERT_PHONE', None)
    if owner_phone:
        try:
            owner_payload = {
                "id": settings.TEXTIT_API_ID,
                "pw": settings.TEXTIT_API_PASSWORD,
                "to": owner_phone,
                "text": f"✅ New CONFIRMED booking!\nHotel: {booking.hotel.name}\nCustomer: {booking.user.username}\nPhone: {customer_phone or 'Not provided'}\nCheck-in: {booking.check_in}\nCheck-out: {booking.check_out}\nTotal: Rs. {booking.amount}\n- SL Booking Hotels"
            }
            owner_response = requests.get(url, params=owner_payload, timeout=10)
            if owner_response.status_code == 200 and "OK" in owner_response.text:
                sms_sent_to_owner = True
        except Exception as e:
            messages.warning(request, f'Owner alert SMS failed: {str(e)}')

    # Success message
    msg = 'Booking confirmed!'
    if sms_sent_to_customer:
        msg += ' SMS sent to customer!'
    if sms_sent_to_owner:
        msg += ' Alert SMS sent to owner!'
    
    messages.success(request, msg)
    return redirect('owner_bookings')

# Reject booking
@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.hotel.owner:
        messages.error(request, 'Access denied.')
        return redirect('owner_bookings')
    booking.status = 'cancelled'
    booking.save()
    messages.success(request, 'Booking rejected.')
    return redirect('owner_bookings')

# Add manual booking
@login_required
def add_manual_booking(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == 'POST':
        form = ManualBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.hotel = hotel
            booking.save()
            messages.success(request, 'Manual booking added!')
            return redirect('owner_bookings')
    else:
        form = ManualBookingForm()
    return render(request, 'core/add_manual_booking.html', {'form': form, 'hotel': hotel})

# Static pages
def about(request):
    return render(request, 'core/about.html')

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

def contact(request):
    if request.method == 'POST':
        # Simple contact form (email send optional)
        messages.success(request, 'Your message has been sent!')
        return redirect('contact')
    return render(request, 'core/contact.html')

def services(request):
    return render(request, 'core/services.html')