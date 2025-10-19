#!/usr/bin/env python3
"""
URL configuration for the listings app.
Defines routes for listings, bookings, reviews, and payment endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ListingViewSet, 
    BookingViewSet, 
    ReviewViewSet,
    PaymentViewSet,
    initiate_payment,
    verify_payment,
    payment_status
)

# Create a router and register viewsets
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'payments', PaymentViewSet, basename='payment')

# Define URL patterns
urlpatterns = [
    # Router URLs (includes all viewsets)
    path('', include(router.urls)),
    
    # Payment endpoints
    path('payments/initiate-payment/', initiate_payment, name='initiate-payment'),
    path('payments/verify-payment/<str:reference>/', verify_payment, name='verify-payment'),
    path('payments/status/<str:reference>/', payment_status, name='payment-status'),
]
