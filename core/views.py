# core/views.py - add these functions
@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.room.hotel.owner == request.user:
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, 'Booking confirmed!')
    return redirect('owner_bookings')

@login_required
def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.room.hotel.owner == request.user:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking rejected!')
    return redirect('owner_bookings')

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled!')
    return redirect('my_bookings')