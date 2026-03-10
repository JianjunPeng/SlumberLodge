from django.contrib import admin
from .models import MotelInfo, Facility, RoomType, Room, Attraction, Booking

admin.site.register(MotelInfo)
admin.site.register(Facility)
admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(Attraction)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'room', 'check_in', 'check_out', 'status', 'total_price')
    list_filter = ('status', 'check_in')
    search_fields = ('customer_name', 'customer_email', 'stripe_payment_intent')
