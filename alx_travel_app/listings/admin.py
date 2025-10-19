#!/usr/bin/env python3
"""
Django admin configuration for listings app.
"""

from django.contrib import admin
from .models import Listing, Booking, Review, Payment


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    """Admin interface for Listing model"""
    list_display = ['title', 'location', 'price_per_night', 'created_at']
    list_filter = ['location', 'created_at']
    search_fields = ['title', 'description', 'location']
    ordering = ['-created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin interface for Booking model"""
    list_display = ['id', 'user', 'listing', 'start_date', 'end_date', 'status', 'total_price']
    list_filter = ['status', 'start_date', 'created_at']
    search_fields = ['user__username', 'listing__title']
    ordering = ['-created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model"""
    list_display = ['user', 'listing', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'listing__title', 'comment']
    ordering = ['-created_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model"""
    list_display = ['booking_reference', 'email', 'amount', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['booking_reference', 'transaction_id', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    readonly_fields = ['transaction_id', 'chapa_reference', 'checkout_url', 'paid_at', 'created_at', 'updated_at']
