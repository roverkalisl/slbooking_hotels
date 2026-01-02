from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Hotel, Room, Booking

# ROLE_CHOICES මෙතන hardcode කරලා තියෙනවා (models.py එකට ඉස්සරහට import වෙන problem නැහැ)
ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('owner', 'Owner'),
)

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    phone_number = forms.CharField(max_length=20, required=False, label="Phone Number (for WhatsApp)")
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="I am a")

    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'role': self.cleaned_data['role'],
                    'phone_number': self.cleaned_data['phone_number']
                }
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