#!/usr/bin/env python3
"""
Celery tasks for the listings app.
Handles asynchronous email notifications and other background tasks.
"""

import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_confirmation_email(
    self,
    email: str,
    first_name: str,
    amount: float,
    transaction_reference: str,
    booking_id: str = None
):
    """
    Send payment confirmation email to customer.
    
    Args:
        email: Customer email address
        first_name: Customer first name
        amount: Payment amount
        transaction_reference: Transaction reference number
        booking_id: Optional booking ID
    """
    try:
        subject = f"Payment Confirmation - {transaction_reference}"
        
        # Create email body
        message = f"""
Dear {first_name},

Thank you for your payment!

Payment Details:
- Transaction Reference: {transaction_reference}
- Amount: ETB {amount:.2f}
- Status: Completed
"""
        
        if booking_id:
            message += f"- Booking ID: {booking_id}\n"
        
        message += """

Your payment has been successfully processed. You will receive a booking confirmation shortly.

If you have any questions, please contact our support team.

Best regards,
ALX Travel App Team
"""
        
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Payment confirmation email sent to {email}")
        return {"status": "success", "email": email}
        
    except Exception as exc:
        logger.error(f"Failed to send confirmation email: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_booking_confirmation_email(
    self,
    email: str,
    first_name: str,
    booking_id: str,
    listing_title: str,
    start_date: str,
    end_date: str,
    total_price: float
):
    """
    Send booking confirmation email to customer.
    
    Args:
        email: Customer email address
        first_name: Customer first name
        booking_id: Booking reference ID
        listing_title: Property title
        start_date: Check-in date
        end_date: Check-out date
        total_price: Total booking price
    """
    try:
        subject = f"Booking Confirmation - {booking_id}"
        
        message = f"""
Dear {first_name},

Your booking has been confirmed!

Booking Details:
- Booking Reference: {booking_id}
- Property: {listing_title}
- Check-in: {start_date}
- Check-out: {end_date}
- Total Amount: ETB {total_price:.2f}

We look forward to hosting you!

Best regards,
ALX Travel App Team
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Booking confirmation email sent to {email}")
        return {"status": "success", "email": email}
        
    except Exception as exc:
        logger.error(f"Failed to send booking confirmation email: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_payment_failure_notification(
    self,
    email: str,
    first_name: str,
    transaction_reference: str,
    amount: float
):
    """
    Send payment failure notification to customer.
    
    Args:
        email: Customer email address
        first_name: Customer first name
        transaction_reference: Transaction reference number
        amount: Payment amount
    """
    try:
        subject = f"Payment Failed - {transaction_reference}"
        
        message = f"""
Dear {first_name},

We're sorry, but your payment could not be processed.

Payment Details:
- Transaction Reference: {transaction_reference}
- Amount: ETB {amount:.2f}
- Status: Failed

Please try again or contact our support team for assistance.

Best regards,
ALX Travel App Team
"""
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        logger.info(f"Payment failure notification sent to {email}")
        return {"status": "success", "email": email}
        
    except Exception as exc:
        logger.error(f"Failed to send payment failure notification: {str(exc)}")
        raise self.retry(exc=exc)


@shared_task
def cleanup_pending_payments():
    """
    Periodic task to cleanup old pending payments.
    Should be run via Celery Beat scheduler.
    """
    from datetime import timedelta
    from django.utils import timezone
    from .models import Payment
    
    try:
        # Find payments pending for more than 24 hours
        cutoff_time = timezone.now() - timedelta(hours=24)
        old_pending_payments = Payment.objects.filter(
            status='Pending',
            created_at__lt=cutoff_time
        )
        
        count = old_pending_payments.count()
        
        # Mark as failed
        old_pending_payments.update(status='Failed')
        
        logger.info(f"Cleaned up {count} old pending payments")
        return {"status": "success", "count": count}
        
    except Exception as exc:
        logger.error(f"Failed to cleanup pending payments: {str(exc)}")
        return {"status": "error", "message": str(exc)}
