# core/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('owner', 'Hotel Owner'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Hotel(models.Model):
    RENTED_TYPE_CHOICES = (
        ('full', 'Full Villa'),
        ('rooms', 'Individual Rooms'),
    )
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')
    address = models.TextField()
    description = models.TextField(blank=True, null=True, help_text="Detailed description of the hotel/villa")
    google_location_link = models.URLField(blank=True, null=True)
    social_media_link = models.URLField(blank=True, null=True)
    rented_type = models.CharField(max_length=20, choices=RENTED_TYPE_CHOICES, default='rooms')
    facilities = models.ManyToManyField(Facility, blank=True)  # tick box facilities
    main_image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                          help_text="Price per night if rented as Full Villa")

    def __str__(self):
        return self.name

class Room(models.Model):
    AC_CHOICES = (
        ('ac', 'Air Conditioned'),
        ('non_ac', 'Non-AC'),
    )
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=50)
    ac_type = models.CharField(max_length=10, choices=AC_CHOICES, default='non_ac')
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_number} ({self.get_ac_type_display()})"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.customer} - {self.room} ({self.check_in} to {self.check_out})"