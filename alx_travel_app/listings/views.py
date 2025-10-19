#!/usr/bin/env python3
"""
API Views for the travel booking application
Includes CRUD operations for listings, bookings, and payment integration
"""

import uuid
import logging
from datetime import datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Listing, Booking, Review, Payment
from .serializers import (
    ListingSerializer, 
    BookingSerializer, 
    ReviewSerializer,
    PaymentSerializer,
    PaymentInitiateSerializer,
    PaymentVerifySerializer
)
from .chapa import initialize_chapa_payment, verify_chapa_payment
from .tasks import send_payment_confirmation_email

logger = logging.getLogger(__name__)


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Listing instances.
    Provides CRUD operations: list, create, retrieve, update, destroy
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['location', 'price_per_night']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['price_per_night', 'created_at']


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Booking instances.
    Provides CRUD operations: list, create, retrieve, update, destroy
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['listing', 'user', 'status']
    ordering_fields = ['created_at', 'start_date']


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Review instances.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['listing', 'user', 'rating']
    ordering_fields = ['created_at', 'rating']


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing Payment instances.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'booking']
    ordering_fields = ['created_at', 'amount']


@api_view(['POST'])
def initiate_payment(request):
    """
    Initiate a payment transaction with Chapa.
    
    POST /api/payments/initiate-payment/
    
    Request body:
    {
        "booking_id": "uuid-optional",
        "amount": 1500.00,
        "email": "customer@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "callback_url": "https://yourapp.com/callback",
        "return_url": "https://yourapp.com/success",
        "currency": "ETB"
    }
    """
    serializer = PaymentInitiateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                "status": "error",
                "message": "Invalid request data",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    
    # Generate unique transaction reference
    tx_ref = f"TX-{uuid.uuid4().hex[:12].upper()}"
    
    try:
        # Get booking if provided
        booking = None
        if data.get('booking_id'):
            try:
                booking = Booking.objects.get(id=data['booking_id'])
            except Booking.DoesNotExist:
                return Response(
                    {
                        "status": "error",
                        "message": "Booking not found"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            booking_reference=tx_ref,
            amount=data['amount'],
            currency=data.get('currency', 'ETB'),
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            callback_url=data['callback_url'],
            return_url=data['return_url'],
            status='Pending'
        )
        
        # Initialize payment with Chapa
        success, chapa_response = initialize_chapa_payment(
            amount=float(data['amount']),
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            tx_ref=tx_ref,
            callback_url=data['callback_url'],
            return_url=data['return_url'],
            currency=data.get('currency', 'ETB')
        )
        
        if success and 'data' in chapa_response:
            # Update payment with Chapa checkout URL
            payment.checkout_url = chapa_response['data'].get('checkout_url')
            payment.chapa_reference = chapa_response['data'].get('tx_ref')
            payment.save()
            
            logger.info(f"Payment initiated successfully: {tx_ref}")
            
            return Response(
                {
                    "status": "success",
                    "message": "Payment initiated successfully",
                    "data": {
                        "checkout_url": payment.checkout_url,
                        "transaction_reference": tx_ref,
                        "payment_id": str(payment.id)
                    }
                },
                status=status.HTTP_200_OK
            )
        else:
            # Mark payment as failed
            payment.status = 'Failed'
            payment.save()
            
            error_msg = chapa_response.get('message', 'Failed to initialize payment')
            logger.error(f"Payment initialization failed: {error_msg}")
            
            return Response(
                {
                    "status": "error",
                    "message": error_msg,
                    "details": chapa_response
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        return Response(
            {
                "status": "error",
                "message": "An error occurred while initiating payment",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def verify_payment(request, reference):
    """
    Verify a payment transaction with Chapa.
    
    GET /api/payments/verify-payment/<reference>/
    """
    try:
        # Get payment record
        payment = get_object_or_404(Payment, booking_reference=reference)
        
        # Verify with Chapa
        success, chapa_response = verify_chapa_payment(reference)
        
        if success and 'data' in chapa_response:
            chapa_data = chapa_response['data']
            chapa_status = chapa_data.get('status', '').lower()
            
            # Update payment based on Chapa response
            if chapa_status == 'success':
                payment.status = 'Completed'
                payment.transaction_id = chapa_data.get('trx_ref')
                payment.payment_method = chapa_data.get('payment_method')
                payment.paid_at = timezone.now()
                payment.save()
                
                # Update booking status if exists
                if payment.booking:
                    payment.booking.status = 'Confirmed'
                    payment.booking.save()
                
                # Send confirmation email asynchronously
                try:
                    send_payment_confirmation_email.delay(
                        email=payment.email,
                        first_name=payment.first_name,
                        amount=float(payment.amount),
                        transaction_reference=reference,
                        booking_id=str(payment.booking.id) if payment.booking else None
                    )
                except Exception as email_error:
                    logger.error(f"Failed to queue confirmation email: {str(email_error)}")
                
                logger.info(f"Payment verified successfully: {reference}")
                
                return Response(
                    {
                        "status": "success",
                        "message": "Payment verified successfully",
                        "data": {
                            "transaction_reference": reference,
                            "status": payment.status,
                            "amount": float(payment.amount),
                            "email": payment.email,
                            "paid_at": payment.paid_at
                        }
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Payment failed
                payment.status = 'Failed'
                payment.save()
                
                # Update booking status if exists
                if payment.booking:
                    payment.booking.status = 'Cancelled'
                    payment.booking.save()
                
                logger.warning(f"Payment verification failed: {reference}")
                
                return Response(
                    {
                        "status": "failed",
                        "message": "Payment verification failed",
                        "data": {
                            "transaction_reference": reference,
                            "status": payment.status
                        }
                    },
                    status=status.HTTP_200_OK
                )
        else:
            error_msg = chapa_response.get('message', 'Verification failed')
            logger.error(f"Chapa verification error: {error_msg}")
            
            return Response(
                {
                    "status": "error",
                    "message": error_msg,
                    "details": chapa_response
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    except Payment.DoesNotExist:
        return Response(
            {
                "status": "error",
                "message": "Payment record not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        return Response(
            {
                "status": "error",
                "message": "An error occurred while verifying payment",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def payment_status(request, reference):
    """
    Get the status of a payment transaction.
    
    GET /api/payments/status/<reference>/
    """
    try:
        payment = get_object_or_404(Payment, booking_reference=reference)
        serializer = PaymentSerializer(payment)
        
        return Response(
            {
                "status": "success",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Payment.DoesNotExist:
        return Response(
            {
                "status": "error",
                "message": "Payment not found"
            },
            status=status.HTTP_404_NOT_FOUND
        )
