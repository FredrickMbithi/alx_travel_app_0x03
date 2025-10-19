#!/usr/bin/env python3
"""
Django models for the travel app.
This file defines the main database tables: Listing, Booking, Review, and Payment.
Each model maps to a table and includes relationships & constraints.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User


class Listing(models.Model):
    """
    A property (hotel, apartment, cabin, etc.) available for booking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Booking(models.Model):
    """
    A booking record made by a user for a listing.
    Connects User → Listing with start/end dates.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} booked {self.listing.title}"
    
    def save(self, *args, **kwargs):
        """Calculate total price based on number of nights and price per night"""
        if self.start_date and self.end_date and self.listing:
            nights = (self.end_date - self.start_date).days
            self.total_price = nights * self.listing.price_per_night
        super().save(*args, **kwargs)


class Review(models.Model):
    """
    A user review for a listing.
    Stores rating + optional comment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} rated {self.listing.title}: {self.rating}/5"


class Payment(models.Model):
    """
    Payment transaction record for bookings.
    Tracks payment status and integrates with Chapa Payment Gateway.
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, 
        on_delete=models.CASCADE, 
        related_name="payments",
        null=True,
        blank=True
    )
    booking_reference = models.CharField(max_length=255, unique=True, db_index=True)
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='ETB')
    email = models.EmailField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Chapa specific fields
    chapa_reference = models.CharField(max_length=255, null=True, blank=True)
    checkout_url = models.URLField(max_length=500, null=True, blank=True)
    
    # Payment details
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    callback_url = models.URLField(max_length=500, null=True, blank=True)
    return_url = models.URLField(max_length=500, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_reference']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Payment {self.booking_reference} - {self.status}"
