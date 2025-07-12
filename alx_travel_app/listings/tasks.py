from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def send_booking_confirmation_email(self, booking_id):
    """
    Background task to send a booking confirmation email.
    Triggered with .delay(booking_id) from the BookingViewSet.
    """
    booking = Booking.objects.select_related('listing', 'user').get(booking_id=booking_id)

    subject = f'Booking Confirmed: {booking.listing.name}'
    message = f"""
Hi {booking.user.first_name or booking.user.username},

Your booking for "{booking.listing.name}" is confirmed.

Check-in: {booking.check_in_date.strftime('%b %d, %Y')}
Check-out: {booking.check_out_date.strftime('%b %d, %Y')}
Guests: {booking.number_of_guests}
Total: ${booking.total_price}

Thank you for booking with us!
""".strip()

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [booking.user.email], fail_silently=False)
