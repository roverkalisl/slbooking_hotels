# core/forms.py
from django import forms import ModelForm, Form
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Hotel, Room, Booking
from django import forms

class RegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES[0:2])  # customer or owner only
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                role=self.cleaned_data['role']
            )
        return user

class HotelForm(ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'location', 'address', 'description', 'image']

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'price_per_night']

class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = ['check_in', 'check_out']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }