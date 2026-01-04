# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('search/', views.search_hotels, name='search_hotels'),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('book-villa/<int:hotel_id>/', views.book_villa, name='book_villa'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/add-hotel/', views.add_hotel, name='add_hotel'),
    path('owner/edit-hotel/<int:hotel_id>/', views.edit_hotel, name='edit_hotel'),
    path('owner/hotel/<int:hotel_id>/add-room/', views.add_room, name='add_room'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
    path('owner/confirm-booking/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('owner/reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('owner/hotel/<int:hotel_id>/add-manual-booking/', views.add_manual_booking, name='add_manual_booking'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),path('about/', views.about, name='about'),
path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
path('contact/', views.contact, name='contact'),
    
   # path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
]