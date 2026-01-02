from django.contrib import admin
from .models import Hotel, Room, Booking, Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone_number']  # 'phone' → 'phone_number'

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'address', 'rented_type']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'room_number', 'room_type', 'ac_type', 'price_per_night']  # 'is_available' delete කරලා

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'user', 'room', 'check_in', 'check_out', 'status', 'amount']  # 'customer' → 'user', 'source' delete කරලා