from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('ads.txt', views.ads_txt),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('search/', views.search_hotels, name='search_hotels'),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('book-villa/<int:hotel_id>/', views.book_villa, name='book_villa'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # Owner paths
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/add-hotel/', views.add_hotel, name='add_hotel'),
    path('owner/edit-hotel/<int:hotel_id>/', views.edit_hotel, name='edit_hotel'),
    path('owner/hotel/<int:hotel_id>/add-room/', views.add_room, name='add_room'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
    path('owner/confirm-booking/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('owner/reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    path('owner/hotel/<int:hotel_id>/add-manual-booking/', views.add_manual_booking, name='add_manual_booking'),
    
    # Static pages
    path('about/', views.about, name='about'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    
    # Logout
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Commented analytics (optional)
    # path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
path('refund-policy/', views.refund_policy, name='refund_policy'),
path('cancellation-policy/', views.cancellation_policy, name='cancellation_policy'),
]