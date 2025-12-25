from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('search/', views.search_hotels, name='search_hotels'),
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('book-villa/<int:hotel_id>/', views.book_villa, name='book_villa'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('owner/add-hotel/', views.add_hotel, name='add_hotel'),
    path('owner/edit-hotel/<int:hotel_id>/', views.edit_hotel, name='edit_hotel'),
    path('owner/hotel/<int:hotel_id>/add-room/', views.add_room, name='add_room'),
]