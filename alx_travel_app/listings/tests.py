from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth.models import User
from .models import Listing, Booking
from .views import BookingViewSet

class BookingViewSetTaskTest(TestCase):
    def setUp(self):
        # create test user and listing
        self.user = User.objects.create_user(username='unit_test_user', email='unit@example.com', password='testpass')
        self.listing = Listing.objects.create(
            title='Unit Test Hotel',
            description='Unit test',
            price_per_night=50.00,
            location='TestCity'
        )

    def test_perform_create_queues_email(self):
        # create a booking instance to be returned by serializer.save()
        booking = Booking.objects.create(
            user=self.user,
            listing=self.listing,
            start_date='2025-12-01',
            end_date='2025-12-03',
            status='Confirmed'
        )

        # Fake serializer with save() returning the booking
        serializer = MagicMock()
        serializer.save.return_value = booking

        # Patch the task importer used by views (module-level import)
        with patch('listings.views.send_booking_confirmation_email') as mock_task:
            viewset = BookingViewSet()
            viewset.perform_create(serializer)

            # Ensure .delay was called with booking id as string
            mock_task.delay.assert_called_once_with(str(booking.id))
