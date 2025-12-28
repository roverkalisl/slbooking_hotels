# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Hotel, Room, Booking
from .forms import RegistrationForm, HotelForm, RoomForm, BookingForm

def home(request):
    hotels = Hotel.objects.all()[:6]  # Featured hotels
    return render(request, 'core/home.html', {'hotels': hotels})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
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
    rooms = hotel.rooms.all() if hotel.rented_type == 'rooms' else None
    is_full_villa = hotel.rented_type == 'full'
    return render(request, 'core/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms,
        'is_full_villa': is_full_villa
    })

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            overlapping = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=['pending', 'confirmed']
            ).exists()
            if overlapping:
                messages.error(request, 'This room is not available for the selected dates.')
            else:
                booking = form.save(commit=False)
                booking.customer = request.user
                booking.room = room
                booking.hotel = room.hotel
                booking.save()
                messages.success(request, 'Booking requested successfully!')
                return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'core/book_room.html', {'form': form, 'room': room})

@login_required
def book_villa(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, rented_type='full')
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data['check_in']
            check_out = form.cleaned_data['check_out']
            overlapping = Booking.objects.filter(
                hotel=hotel,
                check_in__lt=check_out,
                check_out__gt=check_in,
                status__in=['pending', 'confirmed']
            ).exists()
            if overlapping:
                messages.error(request, 'This villa is not available for the selected dates.')
            else:
                booking = form.save(commit=False)
                booking.customer = request.user
                booking.hotel = hotel
                booking.room = None
                booking.save()
                messages.success(request, 'Full Villa booking requested successfully!')
                return redirect('my_bookings')
    else:
        form = BookingForm()
    return render(request, 'core/book_villa.html', {'form': form, 'hotel': hotel})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-id')
    return render(request, 'core/my_bookings.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Your booking has been cancelled.')
    else:
        messages.info(request, 'This booking cannot be cancelled.')
    return redirect('my_bookings')

@login_required
def owner_dashboard(request):
    if request.user.profile.role != 'owner':
        messages.error(request, 'Access denied. Owners only.')
        return redirect('home')
    hotels = Hotel.objects.filter(owner=request.user)
    return render(request, 'core/owner_dashboard.html', {'hotels': hotels})

@login_required
def owner_bookings(request):
    if request.user.profile.role != 'owner':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # All bookings for owner's hotels (rooms + entire villa)
    bookings = Booking.objects.filter(
        Q(room__hotel__owner=request.user) | Q(hotel__owner=request.user, room=None)
    ).order_by('-id')
    
    return render(request, 'core/owner_bookings.html', {'bookings': bookings})

@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        Q(id=booking_id),
        Q(room__hotel__owner=request.user) | Q(hotel__owner=request.user, room=None)
    )
    
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, f'Booking #{booking.id} confirmed successfully!')
    else:
        messages.info(request, 'This booking is already processed.')
    return redirect('owner_bookings')

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        Q(id=booking_id),
        Q(room__hotel__owner=request.user) | Q(hotel__owner=request.user, room=None)
    )
    
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, f'Booking #{booking.id} rejected.')
    else:
        messages.info(request, 'This booking is already processed.')
    return redirect('owner_bookings')

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
            form.save_m2m()  # for facilities
            messages.success(request, 'Hotel added successfully!')
            return redirect('owner_dashboard')
    else:
        form = HotelForm()
    return render(request, 'core/add_hotel.html', {'form': form})

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