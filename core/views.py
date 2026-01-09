from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db.models import Q
from .models import Hotel, Room, Booking, Profile
from .forms import HotelForm, RoomForm, BookingForm, ManualBookingForm
from django.contrib.auth.forms import UserCreationForm
from twilio.rest import Client
from django.conf import settings
from django.views.decorators.cache import never_cache
import requests
from django.conf import settings
from django.http import HttpResponse
# Home page
def home(request):
    hotels = Hotel.objects.all()[:6]  # featured hotels
    return render(request, 'core/home.html', {'hotels': hotels})

# Register
from .forms import RegistrationForm  # මේක import කරන්න (UserCreationForm නෙමෙයි)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # custom save method එක run වෙනවා (email, phone, role save වෙනවා)
            messages.success(request, 'Registration successful!')
            return redirect('login')  # or 'home'
    else:
        form = RegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})

# Search hotels
def search_hotels(request):
    query = request.GET.get('q', '')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    rooms = request.GET.get('rooms', 1)
    
    hotels = Hotel.objects.all()
    
    if query:
        hotels = hotels.filter(
            Q(name__icontains=query) | 
            Q(address__icontains=query)
        )
    
    # Future: check_in/out සහ rooms එක්ක availability filter කරන්න (advanced)
    
    return render(request, 'core/search.html', {
        'hotels': hotels,
        'query': query
    })

# Hotel detail + calendar
def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = hotel.rooms.all() if hotel.rented_type == 'rooms' else None
    is_full_villa = hotel.rented_type == 'full'
    bookings = hotel.bookings.filter(status='confirmed').all()  # calendar එකට confirmed විතරයි
    
    return render(request, 'core/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms,
        'is_full_villa': is_full_villa,
        'bookings': bookings
    })

# Book room
@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = room.hotel
            booking.room = room
            booking.save()
            messages.success(request, 'Booking request sent! Waiting for confirmation.')
            return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'core/book_room.html', {'form': form, 'room': room})

# Book entire villa
@login_required
def book_villa(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.hotel = hotel
            booking.save()
            messages.success(request, 'Booking request sent! Waiting for confirmation.')
            return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'core/book_villa.html', {'form': form, 'hotel': hotel})

# My bookings
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-id')
    return render(request, 'core/my_bookings.html', {'bookings': bookings})

@login_required
def owner_dashboard(request):
    if request.user.profile.role != 'owner':
        messages.error(request, 'Only owners can access this page.')
        return redirect('home')
    
    hotels = Hotel.objects.filter(owner=request.user)
    return render(request, 'core/owner_dashboard.html', {'hotels': hotels})

# Cancel booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled.')
    return redirect('my_bookings')

# Owner dashboard
@login_required
def owner_bookings(request):
    if request.user.profile.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # හැම hotel එකක bookings එකම ගන්න (room එක තියෙන/නැති හැම එකම)
    bookings = Booking.objects.filter(hotel__owner=request.user).order_by('-id')
    
    return render(request, 'core/owner_bookings.html', {'bookings': bookings})
# Add hotel
@login_required
def add_hotel(request):
    if request.user.profile.role != 'owner':
        messages.error(request, 'Only owners can add hotels.')
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
            messages.success(request, 'Hotel updated!')
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
            messages.success(request, 'Room added!')
            return redirect('owner_dashboard')
    else:
        form = RoomForm()
    return render(request, 'core/add_room.html', {'form': form, 'hotel': hotel})

# Owner bookings (confirm/reject)
@login_required
def owner_bookings(request):
    if request.user.profile.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    bookings = Booking.objects.filter(
        Q(room__hotel__owner=request.user) | Q(hotel__owner=request.user, room=None)
    ).order_by('-id')
    
    return render(request, 'core/owner_bookings.html', {'bookings': bookings})

# Confirm booking + payment calculation + WhatsApp
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

    # SMS Alert to Owner
    sms_sent_to_owner = False
    if settings.OWNER_ALERT_PHONE:
        try:
            owner_payload = {
                "id": settings.TEXTIT_API_ID,
                "pw": settings.TEXTIT_API_PASSWORD,
                "to": settings.OWNER_ALERT_PHONE,
                "text": f"✅ New CONFIRMED booking!\nHotel: {booking.hotel.name}\nCustomer: {booking.user.username}\nPhone: {customer_phone or 'Not provided'}\nCheck-in: {booking.check_in}\nCheck-out: {booking.check_out}\nTotal: Rs. {booking.amount}\n- SL Booking Hotels"
            }
            owner_response = requests.get(url, params=owner_payload, timeout=10)
            if owner_response.status_code == 200 and "OK" in owner_response.text:
                sms_sent_to_owner = True
        except Exception as e:
            messages.warning(request, f'Owner alert SMS failed: {str(e)}')

    # Success message
    msg = 'Booking confirmed!'
    if sms_sent_to_customer and sms_sent_to_owner:
        msg += ' SMS sent to customer & owner!'
    elif sms_sent_to_customer:
        msg += ' SMS sent to customer!'
    elif sms_sent_to_owner:
        msg += ' Alert SMS sent to owner!'
    
    messages.success(request, msg)
    return redirect('owner_bookings')
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

# Add manual booking + calculation
@login_required
def add_manual_booking(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == 'POST':
        form = ManualBookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.hotel = hotel
            booking.user = User.objects.get(username=form.cleaned_data['customer_username'])
            # Calculate amount
            nights = (booking.check_out - booking.check_in).days
            price = booking.room.price_per_night if booking.room else hotel.price_per_night
            booking.amount = price * nights
            booking.status = 'confirmed'
            booking.save()
            messages.success(request, 'Manual booking added successfully!')
            return redirect('owner_dashboard')
    else:
        form = ManualBookingForm()
    return render(request, 'core/add_manual_booking.html', {'form': form, 'hotel': hotel})
def about(request):
    return render(request, 'core/about.html')

def privacy_policy(request):
    return render(request, 'core/privacy_policy.html')

@login_required  # optional – login වෙලා තියෙනවා නම්
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # මෙතන email send code එක තියෙනවා නම් try/except දාන්න
        try:
            # email send logic (if any)
            messages.success(request, 'Your message has been sent!')
        except Exception as e:
            messages.error(request, 'Message sending failed. Try again later.')
        return redirect('contact')
    
    return render(request, 'core/contact.html')

def services(request):
    return render(request, 'core/services.html')

@never_cache
def home(request):
    hotels = Hotel.objects.all()[:6]  # featured hotels (first 6)

    # View count (session based)
    if 'view_count' not in request.session:
        request.session['view_count'] = 0
    request.session['view_count'] += 1
    view_count = request.session['view_count']

    return render(request, 'core/home.html', {
        'hotels': hotels,
        'view_count': view_count
    })
def ads_txt(request):
    content = "google.com, pub-7289676285085159, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")