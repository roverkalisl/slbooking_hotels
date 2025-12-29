# core/models.py
from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

FACILITY_CHOICES = (
    ('wifi', 'WiFi'),
    ('parking', 'Parking'),
    ('pool', 'Swimming Pool'),
    ('gym', 'Gym'),
    ('spa', 'Spa'),
    ('restaurant', 'Restaurant'),
    ('bar', 'Bar'),
    ('ac', 'Air Conditioning'),
    ('tv', 'TV'),
    ('hotwater', 'Hot Water'),
)

class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('owner', 'Owner'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Hotel(models.Model):
    RENTED_TYPE_CHOICES = (
        ('rooms', 'Individual Rooms'),
        ('full', 'Entire Villa'),
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.TextField()
    description = models.TextField(blank=True)
    google_location_link = models.URLField(blank=True)
    social_media_link = models.URLField(blank=True)
    rented_type = models.CharField(max_length=10, choices=RENTED_TYPE_CHOICES)
    facilities = MultiSelectField(choices=FACILITY_CHOICES, blank=True)
    main_image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo1 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo2 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo3 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo4 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name

class Room(models.Model):
    AC_TYPE_CHOICES = (
        ('ac', 'Air Conditioned'),
        ('non_ac', 'Non-AC'),
    )
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=100)
    ac_type = models.CharField(max_length=10, choices=AC_TYPE_CHOICES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)

    def __str__(self):
        return f"{self.room_number} - {self.hotel.name}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    source = models.CharField(max_length=50, blank=True, null=True)  # e.g., Booking.com

    def __str__(self):
        return f"Booking {self.id} - {self.hotel.name}"