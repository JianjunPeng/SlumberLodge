from django.shortcuts import render
from .models import MotelInfo, Facility, RoomType, Attraction

def home(request):
    motel_info = MotelInfo.get_solo()
    facilities = Facility.objects.all()
    context = {
        'motel': motel_info,
        'facilities': facilities,
    }
    return render(request, 'motel/home.html', context)

def rooms(request):
    room_types = RoomType.objects.all()
    context = {'room_types': room_types}
    return render(request, 'motel/rooms.html', context)

def hope(request):
    attractions = Attraction.objects.all()
    context = {'attractions': attractions}
    return render(request, 'motel/hope.html', context)

def about(request):
    motel_info = MotelInfo.get_solo()
    context = {'motel': motel_info}
    return render(request, 'motel/about.html', context)

import datetime
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def book(request):
    room_types = RoomType.objects.all()
    selected_room_id = request.GET.get('room', '')
    context = {
        'room_types': room_types,
        'selected_room_id': selected_room_id,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'tomorrow': (timezone.now().date() + datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
    }
    return render(request, 'motel/book.html', context)

def check_availability(request):
    """
    HTMX endpoint to check availability and calculate price.
    """
    room_type_id = request.POST.get('room_type')
    check_in_str = request.POST.get('check_in')
    check_out_str = request.POST.get('check_out')

    if not all([room_type_id, check_in_str, check_out_str]):
        return HttpResponse('<div class="text-red-500 mt-2">Please fill in all fields.</div>')

    try:
        check_in = datetime.datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.datetime.strptime(check_out_str, '%Y-%m-%d').date()
        room_type = RoomType.objects.get(id=room_type_id)
    except (ValueError, RoomType.DoesNotExist):
        return HttpResponse('<div class="text-red-500 mt-2">Invalid input data.</div>')

    if check_in >= check_out:
        return HttpResponse('<div class="text-red-500 mt-2">Check-out must be after check-in.</div>')
    
    if check_in < timezone.now().date():
        return HttpResponse('<div class="text-red-500 mt-2">Check-in cannot be in the past.</div>')

    days = (check_out - check_in).days
    total_price = room_type.base_price * days

    from .models import Room, Booking
    
    # Simple availability check: find a room of type that doesn't overlap
    overlapping_bookings = Booking.objects.filter(
        status__in=['pending', 'confirmed'],
        room__room_type=room_type,
        check_in__lt=check_out,
        check_out__gt=check_in
    ).values_list('room__id', flat=True)

    available_rooms = Room.objects.filter(room_type=room_type, is_active=True).exclude(id__in=overlapping_bookings)

    if not available_rooms.exists():
        return HttpResponse('<div class="text-red-500 mt-2 font-semibold flex items-center"><svg class="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg> No rooms available for these dates.</div>')

    context = {
        'available': True,
        'room_type': room_type,
        'check_in': check_in_str,
        'check_out': check_out_str,
        'days': days,
        'total_price': total_price,
    }
    return render(request, 'motel/partials/availability_result.html', context)

from django.shortcuts import redirect
from django.db import transaction

def create_checkout_session(request):
    if request.method != 'POST':
        return redirect('book')

    room_type_id = request.POST.get('room_type')
    check_in_str = request.POST.get('check_in')
    check_out_str = request.POST.get('check_out')
    customer_name = request.POST.get('customer_name')
    customer_email = request.POST.get('customer_email')
    customer_phone = request.POST.get('customer_phone')

    try:
        check_in = datetime.datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.datetime.strptime(check_out_str, '%Y-%m-%d').date()
        room_type = RoomType.objects.get(id=room_type_id)
    except (ValueError, RoomType.DoesNotExist):
        return redirect('book')

    days = (check_out - check_in).days
    total_price = room_type.base_price * days

    from .models import Room, Booking

    # Lock processing: find an available room and create a pending booking
    with transaction.atomic():
        overlapping_bookings = Booking.objects.filter(
            status__in=['pending', 'confirmed'],
            room__room_type=room_type,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).select_for_update().values_list('room__id', flat=True)

        available_rooms = Room.objects.filter(
            room_type=room_type, is_active=True
        ).exclude(id__in=overlapping_bookings).select_for_update()

        if not available_rooms.exists():
            return HttpResponse("No rooms available. Please try different dates.")

        room = available_rooms.first()

        # Create pending booking
        booking = Booking.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            room=room,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            status='pending'
        )

    # Stripe checkout session
    domain_url = request.build_absolute_uri('/')[:-1] # Remove trailing slash
    
    # We catch Stripe errors, but for prototype we just assume valid mock keys
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=customer_email,
            client_reference_id=booking.id,
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(total_price * 100),
                        'product_data': {
                            'name': f"{room_type.name} - {days} night(s)",
                            'description': f"Check-in: {check_in_str} | Check-out: {check_out_str}",
                        },
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=domain_url + '/booking/success/',
            cancel_url=domain_url + '/booking/cancel/',
        )
        booking.stripe_payment_intent = checkout_session.id
        booking.save()
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        booking.status = 'cancelled'
        booking.save()
        return HttpResponse(f"Error creating checkout session: {str(e)}")

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        client_reference_id = session.get('client_reference_id')

        from .models import Booking
        try:
            booking = Booking.objects.get(id=client_reference_id)
            booking.status = 'confirmed'
            booking.save()
            # Here we could send a confirmation email
        except Booking.DoesNotExist:
            pass

    return HttpResponse(status=200)

def booking_success(request):
    return render(request, 'motel/booking_success.html')

def booking_cancel(request):
    return render(request, 'motel/booking_cancel.html')
