from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Hotel, Room, Booking, Profile

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, label="I am a")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )
        return user

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'description', 'main_image', 'photo1', 'photo2', 'photo3', 'photo4', 'facilities', 'rented_type', 'price_per_night']

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
    customer_username = forms.CharField(max_length=150, label="Customer Username")

    class Meta:
        model = Booking
        fields = ['check_in', 'check_out', 'room']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }