from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField

# Role choices
ROLE_CHOICES = (
    ('customer', 'Customer'),
    ('owner', 'Owner'),
)

# Rented type choices
RENTED_TYPE_CHOICES = (
    ('rooms', 'Individual Rooms'),
    ('full', 'Entire Villa'),
)

# AC type choices
AC_TYPE_CHOICES = (
    ('ac', 'AC'),
    ('non_ac', 'Non-AC'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # WhatsApp number +94xxxxxxxxx

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
    facilities = MultiSelectField(choices=[
        ('wifi', 'Free WiFi'),
        ('pool', 'Swimming Pool'),
        ('parking', 'Parking'),
        ('restaurant', 'Restaurant'),
        ('ac', 'Air Conditioning'),
        ('gym', 'Gym'),
        ('spa', 'Spa'),
    ], blank=True)
    rented_type = models.CharField(max_length=20, choices=RENTED_TYPE_CHOICES, default='rooms')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # for full villa

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
        return f"{self.room_number} - {self.room_type}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name} ({self.status})"