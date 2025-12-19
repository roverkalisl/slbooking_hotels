# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Hotel, Room, Booking, Profile
from .forms import RegistrationForm, HotelForm, RoomForm, BookingForm

def home(request):
    hotels = Hotel.objects.all()[:6]  # Featured hotels 6ක්
    return render(request, 'core/home.html', {'hotels': hotels})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = form.cleaned_data['role']
            profile.phone = form.cleaned_data.get('phone')
            profile.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def search_hotels(request):
    query = request.GET.get('q', '')
    hotels = Hotel.objects.all()
    if query:
        hotels = hotels.filter(Q(name__icontains=query) | Q(address__icontains=query))
    return render(request, 'core/search.html', {'hotels': hotels, 'query': query})

def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = hotel.rooms.filter(is_available=True)
    return render(request, 'core/hotel_detail.html', {'hotel': hotel, 'rooms': rooms})

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.room = room
            booking.save()
            room.is_available = False
            room.save()
            messages.success(request, 'Booking requested!')
            return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'core/book_room.html', {'form': form, 'room': room})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user)
    return render(request, 'core/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if booking.status != 'cancelled':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled!')
    return redirect('my_bookings')

@login_required
def owner_dashboard(request):
    if request.user.profile.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    hotels = Hotel.objects.filter(owner=request.user)
    return render(request, 'core/owner_dashboard.html', {'hotels': hotels})

@login_required
def add_hotel(request):
    if request.user.profile.role != 'owner':
        messages.error(request, 'Only hotel owners can add hotels.')
        return redirect('home')
    
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.save()
            form.save_m2m()  # facilities manytomany සඳහා (ඔයාගේ model එකේ facilities manytomany නම්)
            messages.success(request, 'Hotel added successfully!')
            return redirect('owner_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = HotelForm()
    
    return render(request, 'core/add_hotel.html', {'form': form})

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
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RoomForm()
    
    return render(request, 'core/add_room.html', {'form': form, 'hotel': hotel})

@login_required
def owner_bookings(request):
    if request.user.profile.role != 'owner':
        return redirect('home')
    hotels = Hotel.objects.filter(owner=request.user)
    bookings = Booking.objects.filter(room__hotel__in=hotels)
    return render(request, 'core/owner_bookings.html', {'bookings': bookings})

@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.room.hotel.owner == request.user:
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, 'Booking confirmed!')
    return redirect('owner_bookings')

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.room.hotel.owner == request.user:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking rejected!')
    return redirect('owner_bookings')