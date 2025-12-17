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

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hotels')
    address = models.TextField()
    google_location_link = models.URLField(blank=True, null=True)
    social_media_link = models.URLField(blank=True, null=True)
    rented_type = models.CharField(max_length=20, choices=(('full', 'Full Villa'), ('rooms', 'Individual Rooms')))
    facilities = models.TextField(blank=True)
    main_image = models.ImageField(upload_to='hotels/', blank=True, null=True)
       # ... ඉතුරු fields ...
    #main_image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    additional_images = models.ImageField(upload_to='hotels/extra/', blank=True, null=True)  # ← අලුත් field එක add කරලා

    def __str__(self):
        return self.name

    def __str__(self):
        return self.name

class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.room_number}"

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, default='pending', choices=(('pending', 'Pending'), ('confirmed', 'Confirmed')))

    def __str__(self):
        return f"{self.customer} - {self.room} ({self.check_in} to {self.check_out})"