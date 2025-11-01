"""
Celery tasks for the listings app.

These tasks run asynchronously in the background via Celery workers.
"""

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_booking_confirmation_email(self, booking_id):
    """
    Send booking confirmation email to guest.
    
    Args:
        booking_id: ID of the booking
    
    Returns:
        str: Success message
    
    This task:
    1. Fetches booking details from database
    2. Composes email with booking information
    3. Sends email asynchronously
    4. Retries up to 3 times if it fails
    """
    try:
        # Import here to avoid circular imports
        from .models import Booking
        
        # Fetch booking. Use select_related to bring in listing and user
        try:
            booking = Booking.objects.select_related('listing', 'user').get(id=booking_id)
        except Booking.DoesNotExist:
            logger.error(f"Booking {booking_id} not found")
            return f"Booking {booking_id} not found"

        # Calculate nights using model fields
        try:
            nights = (booking.end_date - booking.start_date).days
        except Exception:
            nights = None

        # Guest info (fall back to user.username/email if available)
        guest_name = getattr(booking.user, 'get_full_name', None)
        if callable(guest_name):
            guest_name = booking.user.get_full_name() or booking.user.username
        else:
            guest_name = getattr(booking.user, 'username', 'Guest')

        guest_email = getattr(booking.user, 'email', None)
        if not guest_email:
            # No user email available, can't send
            logger.error(f"Booking {booking_id} has no associated user email")
            return f"No recipient email for booking {booking_id}"

        # Compose email subject
        subject = f'Booking Confirmation - {booking.listing.title}'

        # Compose email message using available fields
        message = f"""
Dear {guest_name},

Thank you for your booking! We're excited to host you.

📋 BOOKING DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking ID:       #{booking.id}
Property:         {booking.listing.title}
Location:         {booking.listing.location}

Check-in:         {booking.start_date.strftime('%B %d, %Y') if booking.start_date else 'TBA'}
Check-out:        {booking.end_date.strftime('%B %d, %Y') if booking.end_date else 'TBA'}
Duration:         {f"{nights} night{'s' if nights and nights != 1 else ''}" if nights is not None else 'TBA'}

Price per night:  ${booking.listing.price_per_night}
Total Amount:     ${booking.total_price if booking.total_price is not None else 'TBA'}
Status:           {booking.status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Property Address:
{booking.listing.location}

📞 Need Help?
If you have any questions, please contact us at support@travelapp.com

We look forward to welcoming you!

Best regards,
The Travel App Team

---
This is an automated message. Please do not reply to this email.
Booking created on: {booking.created_at.strftime('%B %d, %Y at %I:%M %p')}
        """.strip()

        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[guest_email],
            fail_silently=False,
        )

        logger.info(f"Booking confirmation email sent to {guest_email} for booking #{booking_id}")
        return f"Email sent successfully to {guest_email}"
    
    except Exception as exc:
        # Log the error
        logger.error(f"Failed to send booking confirmation email: {str(exc)}")
        
        # Retry the task (exponential backoff)
        # Retry after 60 seconds, then 120, then 180
        retry_delay = 60 * (self.request.retries + 1)
        raise self.retry(exc=exc, countdown=retry_delay)


@shared_task
def send_booking_cancellation_email(booking_id):
    """
    Send booking cancellation notification.
    
    Args:
        booking_id: ID of the cancelled booking
    """
    try:
        from .models import Booking
        
        booking = Booking.objects.select_related('listing').get(id=booking_id)
        
        subject = f'Booking Cancelled - {booking.listing.title}'
        message = f"""
Dear {booking.guest_name},

Your booking has been cancelled.

Booking ID: #{booking.id}
Property: {booking.listing.title}
Check-in: {booking.check_in.strftime('%B %d, %Y')}
Check-out: {booking.check_out.strftime('%B %d, %Y')}

If you did not request this cancellation, please contact us immediately.

Best regards,
The Travel App Team
        """.strip()
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.guest_email],
            fail_silently=False,
        )
        
        logger.info(f"Cancellation email sent for booking #{booking_id}")
        return f"Cancellation email sent to {booking.guest_email}"
    
    except Exception as e:
        logger.error(f"Failed to send cancellation email: {str(e)}")
        raise


@shared_task
def cleanup_old_bookings():
    """
    Periodic task to clean up old completed bookings.
    This can be scheduled with Celery Beat.
    """
    try:
        from .models import Booking
        from datetime import timedelta
        
        # Delete bookings older than 1 year and completed
        cutoff_date = timezone.now() - timedelta(days=365)
        old_bookings = Booking.objects.filter(
            status='Completed',
            created_at__lt=cutoff_date
        )
        
        count = old_bookings.count()
        old_bookings.delete()
        
        logger.info(f"Cleaned up {count} old bookings")
        return f"Deleted {count} old bookings"
    
    except Exception as e:
        logger.error(f"Failed to cleanup old bookings: {str(e)}")
        raise


@shared_task(bind=True)
def test_celery_task(self):
    """
    Simple test task to verify Celery is working.
    Usage: from listings.tasks import test_celery_task
           test_celery_task.delay()
    """
    logger.info("Test task executed successfully!")
    return "Celery is working! ✓"


@shared_task
def send_payment_confirmation_email(email: str, first_name: str, amount: float, transaction_reference: str, booking_id: str = None):
    """
    Send a payment confirmation email. This is a simple wrapper task used by
    the payment verification flow. It accepts primitive args so it can be
    queued reliably from views.
    """
    try:
        subject = f'Payment Confirmation - {transaction_reference}'
        message = f"""
Dear {first_name},

Thank you for your payment.

Transaction Reference: {transaction_reference}
Amount: {amount}

If this payment corresponds to a booking (ID: {booking_id}), your booking
will be updated shortly.

Best regards,
The Travel App Team
        """.strip()

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        logger.info(f"Payment confirmation email sent to {email} for tx {transaction_reference}")
        return f"Payment email sent to {email}"
    except Exception as exc:
        logger.error(f"Failed to send payment confirmation email: {exc}")
        raise