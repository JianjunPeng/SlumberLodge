from django.db import models
from django.contrib.auth.models import User

class MotelInfo(models.Model):
    name = models.CharField(max_length=100, default="Slumber Lodge Motel")
    address = models.CharField(max_length=255, default="250 Fort St, Hope, BC V0X 1L0")
    phone = models.CharField(max_length=20, default="+1 (604) 869-5999")
    email = models.EmailField(default="info@slumberlodgehope.ca")
    welcome_message = models.TextField(blank=True, default="Welcome to Slumber Lodge in beautiful Hope, BC.")
    about_text = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="motel_images/", null=True, blank=True)

    def save(self, *args, **kwargs):
        # Enforce singleton
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.name

class Facility(models.Model):
    name = models.CharField(max_length=100)
    icon_name = models.CharField(max_length=50, blank=True, help_text="Tailwind heroicon name or similar")

    def __str__(self):
        return self.name

class RoomType(models.Model):
    name = models.CharField(max_length=100)
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField()
    bed_config = models.CharField(max_length=100, help_text="e.g., 2 Queen Beds")
    capacity = models.PositiveIntegerField(default=2)
    image = models.ImageField(upload_to="room_images/", null=True, blank=True)
    
    def __str__(self):
        return self.name

class Room(models.Model):
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='rooms')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.room_number} ({self.room_type.name})"

class Attraction(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    image = models.ImageField(upload_to="attraction_images/", null=True, blank=True)
    distance_notes = models.CharField(max_length=100, blank=True, help_text="e.g., 5 mins walk")

    def __str__(self):
        return self.name

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.room.room_number} ({self.check_in} to {self.check_out})"

class SiteSettings(models.Model):
    logo = models.ImageField(upload_to="site_images/", null=True, blank=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Site Settings"
