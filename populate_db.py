import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slumber_lodge.settings')
django.setup()

from motel.models import MotelInfo, Facility, RoomType, Room, Attraction
from decimal import Decimal

# Motel Info
info = MotelInfo.get_solo()
info.name = "Slumber Lodge"
info.welcome_message = "Your gateway to the majestic Cascade Mountains."
info.about_text = "Established in 1968, Slumber Lodge is Hope's premier destination for travelers seeking comfort and convenience. We pride ourselves on clean rooms and friendly service."
info.save()

# Facilities
Facility.objects.get_or_create(name="Free Wi-Fi", icon_name="wifi")
Facility.objects.get_or_create(name="Free Parking", icon_name="truck")
Facility.objects.get_or_create(name="Pet Friendly", icon_name="paw")
Facility.objects.get_or_create(name="Air Conditioning", icon_name="snow")

# Room Types and Rooms
rt_queen, created = RoomType.objects.get_or_create(
    name="Standard Queen",
    defaults={
        "base_price": Decimal("99.00"),
        "description": "A cozy room featuring one queen bed, flat-screen TV, mini-fridge, and microwave. Perfect for solo travelers or couples.",
        "bed_config": "1 Queen Bed",
        "capacity": 2
    }
)
if created:
    Room.objects.create(room_number="101", room_type=rt_queen)
    Room.objects.create(room_number="102", room_type=rt_queen)

rt_double_queen, created = RoomType.objects.get_or_create(
    name="Double Queen",
    defaults={
        "base_price": Decimal("129.00"),
        "description": "Spacious room with two queen beds. Ideal for families or groups exploring the beautiful nature of Hope, BC.",
        "bed_config": "2 Queen Beds",
        "capacity": 4
    }
)
if created:
    Room.objects.create(room_number="201", room_type=rt_double_queen)
    Room.objects.create(room_number="202", room_type=rt_double_queen)

# Attractions
Attraction.objects.get_or_create(
    name="Othello Tunnels",
    defaults={
        "description": "Historic train tunnels carved through solid granite, featuring spectacular views of the Coquihalla River.",
        "distance_notes": "10 mins drive"
    }
)
Attraction.objects.get_or_create(
    name="Kawkawa Lake",
    defaults={
        "description": "A beautiful lake perfect for swimming, boating, and picnicking during the summer months.",
        "distance_notes": "5 mins drive"
    }
)

print("Database populated successfully!")
