from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

# Choices
ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('owner', 'Owner'),
)

RENTED_TYPE_CHOICES = (
    ('rooms', 'Individual Rooms'),
    ('full', 'Entire Villa'),
)

AC_TYPE_CHOICES = (
    ('ac', 'AC'),
    ('non_ac', 'Non-AC'),
)

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('cancelled', 'Cancelled'),
)

FACILITIES_CHOICES = (
    ('wifi', 'WiFi'),
    ('pool', 'Swimming Pool'),
    ('parking', 'Parking'),
    ('restaurant', 'Restaurant'),
    ('spa', 'Spa'),
    ('gym', 'Gym'),
    ('bar', 'Bar'),
    ('ac', 'Air Conditioning'),
    ('tv', 'TV'),
    ('hot_water', 'Hot Water'),
    ('room_service', 'Room Service'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Hotel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    description = models.TextField()
    main_image = models.ImageField(upload_to='hotels/')
    photo1 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo2 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo3 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo4 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    facilities = MultiSelectField(choices=FACILITIES_CHOICES, blank=True)
    rented_type = models.CharField(max_length=20, choices=RENTED_TYPE_CHOICES, default='rooms')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    google_location_link = models.URLField(blank=True, null=True, verbose_name="Google Maps Link")
    facebook_page = models.URLField(blank=True, null=True, verbose_name="Facebook Page Link")

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=100)
    ac_type = models.CharField(max_length=20, choices=AC_TYPE_CHOICES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)

    def __str__(self):
        return f"{self.room_number} - {self.hotel.name}"

class Booking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} ({self.status})"

class SiteStats(models.Model):
    total_views = models.BigIntegerField(default=0)

    def __str__(self):
        return f"Total Views: {self.total_views}"