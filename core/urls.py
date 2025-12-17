# core/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Customer URLs
    path('search/', views.search_hotels, name='search_hotels'),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),

    # Hotel Owner URLs
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/add-hotel/', views.add_hotel, name='add_hotel'),
    path('owner/hotel/<int:hotel_id>/add-room/', views.add_room, name='add_room'),
    path('owner/bookings/', views.owner_bookings, name='owner_bookings'),
    path('owner/booking/<int:booking_id>/confirm/', views.confirm_booking, name='confirm_booking'),
    # core/urls.py
path('owner/booking/<int:booking_id>/confirm/', views.confirm_booking, name='confirm_booking'),
path('owner/booking/<int:booking_id>/reject/', views.reject_booking, name='reject_booking'),
path('booking/<int:booking_id>/cancel/', views.cancel_booking, name='cancel_booking'),
]