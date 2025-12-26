from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('owner', 'Hotel Owner'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True, null=True, help_text="Contact number")

    def __str__(self):
        return f"{self.user.username} - {self.role}"

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
    description = models.TextField(blank=True, null=True)
    google_location_link = models.URLField(blank=True, null=True)
    social_media_link = models.URLField(blank=True, null=True)
    rented_type = models.CharField(max_length=20, choices=RENTED_TYPE_CHOICES, default='rooms')
    facilities = models.ManyToManyField(Facility, blank=True)
    #main_image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    main_image = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo1 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo2 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo3 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    photo4 = models.ImageField(upload_to='hotels/', blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

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
        return f"{self.hotel.name} - {self.room_number}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)  # for full villa
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            days = (self.check_out - self.check_in).days
            if self.room:
                price = self.room.price_per_night
            elif self.hotel:
                price = self.hotel.price_per_night or 0
            else:
                price = 0
            self.total_price = days * price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.customer} - {self.hotel or self.room.hotel}"