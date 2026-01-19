from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Hotel, Room, Booking, Profile
from .models import Profile, ROLE_CHOICES  # මේක add කරන්න

# Custom Registration Form (email, phone, role එක්ක)
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")
    phone_number = forms.CharField(max_length=20, required=False, label="Phone Number (optional for WhatsApp)")
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True, label="I am a")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control form-control-lg'})
        self.fields['email'].widget.attrs.update({'class': 'form-control form-control-lg'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control form-control-lg'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control form-control-lg'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        # Profile create කරන්න
        Profile.objects.create(
            user=user,
            phone_number=self.cleaned_data.get("phone_number", ""),
            role=self.cleaned_data["role"]
        )
        return user

# Hotel Form
class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = [
            'name', 'address', 'description', 'main_image', 'photo1', 'photo2', 'photo3', 'photo4',
            'facilities', 'rented_type', 'price_per_night', 'google_location_link', 'facebook_page'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'facilities': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# Room Form
class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_number', 'room_type', 'ac_type', 'price_per_night', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

# Manual Booking Form
class ManualBookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['user', 'check_in', 'check_out', 'status']
        widgets = {
            'check_in': forms.DateInput(attrs={'type': 'date'}),
            'check_out': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all()  # all users select කරන්න පුළුවන්
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})