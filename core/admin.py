# core/admin.py
from django.contrib import admin
from .models import Profile, Hotel, Room, Booking

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'location']
    list_filter = ['location']
    search_fields = ['name', 'location']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hotel', 'room_type', 'price_per_night', 'is_available']
    list_filter = ['hotel', 'room_type']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer', 'room', 'check_in', 'check_out', 'status']
    list_filter = ['status', 'check_in']