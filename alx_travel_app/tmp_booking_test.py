import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE','alx_travel_app.settings')
django.setup()
from django.contrib.auth.models import User
from listings.models import Listing, Booking
from datetime import date, timedelta

# Create test user/listing/booking
user, created = User.objects.get_or_create(username='testuser', defaults={'email':'testuser@example.com'})
if created:
    user.set_password('testpass')
    user.save()

listing, _ = Listing.objects.get_or_create(
    title='Test Hotel',
    defaults={
        'description':'Test description',
        'price_per_night':100.00,
        'location':'Nairobi'
    }
)

booking = Booking.objects.create(
    user=user,
    listing=listing,
    start_date=date.today() + timedelta(days=7),
    end_date=date.today() + timedelta(days=10),
    status='Confirmed'
)

from listings.tasks import send_booking_confirmation_email
r = send_booking_confirmation_email.delay(str(booking.id))
print('Dispatched booking confirmation task id:', r.id, 'booking id:', booking.id)
