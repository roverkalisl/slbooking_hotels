# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Hotel, Room, Booking

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.phone = self.cleaned_data.get('phone')
            profile.save()
        return user

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'google_location_link', 'social_media_link', 'rented_type', 'facilities', 'main_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'facilities': forms.Textarea(attrs={'rows': 3}),
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