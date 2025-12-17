# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Hotel, Room, Booking

class RegistrationForm(UserCreationForm):
    # ... same as before ...

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'google_location_link', 'social_media_link', 'rented_type', 'facilities', 'main_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'facilities': forms.CheckboxSelectMultiple(),  # tick box
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price_per_night', 'image']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }