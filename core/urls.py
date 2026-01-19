from django.urls import path
from . import views  # මේක තියෙනවා නම් good

urlpatterns = [
    # Home & Search
    path('', views.home, name='home'),
    path('search/', views.search_hotels, name='search_hotels'),

    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),

    # Hotel & Booking
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('book-room/<int:room_id>/', views.book_room, name='book_room'),
    path('book-villa/<int:hotel_id>/', views.book_villa, name='book_villa'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),

    # Owner Panel
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
    path('owner/add-hotel/', views.add_hotel, name='add_hotel'),
    path('owner/edit-hotel/<int:hotel_id>/', views.edit_hotel, name='edit_hotel'),
    path('owner/add-room/<int:hotel_id>/', views.add_room, name='add_room'),
    path('owner/add-manual-booking/<int:hotel_id>/', views.add_manual_booking, name='add_manual_booking'),

    # Manager Panel
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),

    # Booking Actions
    path('confirm-booking/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),

    # Static Pages
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('cancellation-policy/', views.cancellation_policy, name='cancellation_policy'),
    path('contact/', views.contact, name='contact'),

    # Ads.txt
    path('ads.txt', views.ads_txt, name='ads_txt'),

    # API Endpoints (views.py එකේ තියෙන API views use කරලා)
    path('api/owner/bookings/', views.owner_bookings_api, name='api_owner_bookings'),
    path('api/owner/hotels/', views.owner_hotels_api, name='api_owner_hotels'),
]