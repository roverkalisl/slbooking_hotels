from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Hotel, Room, Booking

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2', 'role']

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'description', 'google_location_link', 'social_media_link', 
                  'rented_type', 'facilities', 'main_image', 'photo1', 'photo2', 'photo3', 'photo4', 'price_per_night']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'facilities': forms.CheckboxSelectMultiple(),
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'ac_type', 'price_per_night', 'image']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }
class ManualBookingForm(forms.ModelForm):
    source = forms.CharField(max_length=50, required=True, initial="Booking.com")
    
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'source']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'check_out': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'source': forms.TextInput(attrs={'class': 'form-control'}),
        }