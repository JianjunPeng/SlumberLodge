from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.rooms, name='rooms'),
    path('hope/', views.hope, name='hope'),
    path('about/', views.about, name='about'),
    path('book/', views.book, name='book'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('booking/success/', views.booking_success, name='booking_success'),
    path('booking/cancel/', views.booking_cancel, name='booking_cancel'),
]
