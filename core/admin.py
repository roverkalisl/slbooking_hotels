# core/admin.py
from django.contrib import admin
from .models import Profile, Hotel, Room, Booking

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone']
    search_fields = ['user__username']

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'rented_type', 'price_per_night']
    list_filter = ['rented_type', 'owner']
    search_fields = ['name', 'address']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hotel', 'room_type', 'ac_type', 'price_per_night', 'is_available']
    list_filter = ['ac_type', 'hotel']
    search_fields = ['room_number', 'room_type']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'hotel', 'room', 'customer', 'check_in', 'check_out', 'status', 'source']
    list_filter = ['status', 'hotel', 'check_in']
    search_fields = ['hotel__name', 'customer__username']