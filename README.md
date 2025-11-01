# Milestone 4: Payment Integration with Chapa API# ALX Travel App 0x00

This Django travel booking application integrates the **Chapa Payment Gateway** to handle secure payment processing for travel bookings.This project defines models for Listings, Bookings, and Reviews, and includes

serializers plus a custom seeder command.

## 🚀 Features

## Setup

- ✅ Payment initiation with Chapa API1. Install requirements:

- ✅ Payment verification and status tracking ```bash

- ✅ Secure transaction handling pip install -r requirements.txt

- ✅ Confirmation emails after successful payments
- ✅ Asynchronous email processing with Celery
- ✅ Comprehensive error handling for failed transactions

## 📋 Prerequisites

- Python 3.8+
- Django 4.x
- PostgreSQL or SQLite
- Redis (for Celery)
- Chapa Developer Account

## 🔧 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/FredrickMbithi/alx_travel_app_0x02.git
cd alx_travel_app_0x02/alx_travel_app
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (example values):

```env
# Django Settings
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Chapa API Credentials
CHAPA_SECRET_KEY=your_chapa_secret_key
CHAPA_PUBLIC_KEY=your_chapa_public_key
CHAPA_BASE_URL=https://api.chapa.co/v1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password

# Celery / Broker (RabbitMQ) Configuration
# Using RabbitMQ (recommended for this project)
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//
CELERY_RESULT_BACKEND=rpc://
```

### 5. Get Chapa API Credentials

1. Visit [Chapa Developer Portal](https://developer.chapa.co/)
2. Create an account
3. Navigate to API Keys section
4. Copy your **Secret Key** and **Public Key**
5. Add them to your `.env` file

### 6. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 7. Seed Sample Data (Optional)

```bash
python manage.py seed
```

### 8. Start message broker (RabbitMQ)

This project uses RabbitMQ as the Celery broker by default. Start RabbitMQ using the system package or Docker.

```bash
# System (Ubuntu/Debian)
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# Docker (recommended for portability)
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# On Mac with Homebrew
# brew services start rabbitmq
```

### 9. Start Celery Worker

Start a Celery worker from the `alx_travel_app` package directory. For development you can use the console email backend so emails are printed to the worker log instead of being sent.

```bash
# From the project package directory
cd alx_travel_app
source ../venv/bin/activate

# Development (prints emails to Celery stdout)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend celery -A alx_travel_app worker --loglevel=info

# Production (use credentials in .env and a real email backend)
celery -A alx_travel_app worker --loglevel=info
```

### 10. Run Development Server

```bash
python manage.py runserver
```

## 📡 API Endpoints

### Payment Endpoints

#### 1. Initiate Payment

**POST** `/api/payments/initiate-payment/`

Creates a new payment transaction and returns the Chapa checkout URL.

**Request Body:**

```json
{
  "booking_id": "uuid-of-booking",
  "email": "customer@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "amount": 1500.0,
  "callback_url": "https://yourapp.com/payment/callback",
  "return_url": "https://yourapp.com/payment/success"
}
```

**Response:**

```json
{
  "status": "success",
  "message": "Payment initiated successfully",
  "data": {
    "checkout_url": "https://checkout.chapa.co/checkout/web/payment/UUID",
    "transaction_reference": "TX-1234567890"
  }
}
```

#### 2. Verify Payment

**GET** `/api/payments/verify-payment/<transaction_reference>/`

Verifies the payment status with Chapa and updates the database.

**Response (Success):**

```json
{
  "status": "success",
  "message": "Payment verified successfully",
  "data": {
    "transaction_reference": "TX-1234567890",
    "status": "Completed",
    "amount": 1500.0,
    "email": "customer@example.com"
  }
}
```

**Response (Failed):**

```json
{
  "status": "failed",
  "message": "Payment verification failed",
  "data": {
    "transaction_reference": "TX-1234567890",
    "status": "Failed"
  }
}
```

### Booking Endpoints

#### 3. List Bookings

**GET** `/api/bookings/`

#### 4. Create Booking

**POST** `/api/bookings/`

### Listing Endpoints

#### 5. List Listings

**GET** `/api/listings/`

#### 6. Get Listing Details

**GET** `/api/listings/<listing_id>/`

## 🔄 Payment Workflow

```
1. User creates a booking
   ↓
2. Frontend calls /initiate-payment/ endpoint
   ↓
3. Backend creates Payment record (status: Pending)
   ↓
4. Backend calls Chapa API to initialize transaction
   ↓
5. Chapa returns checkout URL
   ↓
6. User redirected to Chapa checkout page
   ↓
7. User completes payment
   ↓
8. Chapa redirects to callback URL
   ↓
9. Frontend calls /verify-payment/<reference>/
   ↓
10. Backend verifies transaction with Chapa API
   ↓
11. If successful:
    - Update Payment status to "Completed"
    - Update Booking status to "Confirmed"
    - Send confirmation email (async via Celery)
    ↓
12. If failed:
    - Update Payment status to "Failed"
    - Update Booking status to "Cancelled"
```

## 🧪 Testing

### Test Environment

Use Chapa's sandbox environment for testing:

```env
CHAPA_BASE_URL=https://api.chapa.co/v1  # Sandbox URL
```

### Test Cards

Use Chapa's test card numbers for successful/failed transactions:

- **Successful Payment**: Use valid test card details from Chapa documentation
- **Failed Payment**: Use declined test card details

### Test Scenarios

1. **Successful Payment Flow**

   - Initiate payment
   - Complete checkout with test card
   - Verify payment status
   - Check database for status update
   - Verify confirmation email sent

2. **Failed Payment Flow**
   - Initiate payment
   - Use declined test card
   - Verify payment status
   - Check database shows "Failed" status

### Sample Test Results

#### Payment Initiation

```
Request: POST /api/payments/initiate-payment/
Status: 200 OK
Response Time: 1.2s
✓ Payment record created in database
✓ Chapa checkout URL returned
```

#### Payment Verification (Success)

```
Request: GET /api/payments/verify-payment/TX-1234567890/
Status: 200 OK
Response Time: 0.8s
✓ Payment status updated to "Completed"
✓ Booking status updated to "Confirmed"
✓ Confirmation email queued for sending
```

#### Payment Verification (Failure)

```
Request: GET /api/payments/verify-payment/TX-9876543210/
Status: 200 OK
Response Time: 0.7s
✓ Payment status updated to "Failed"
✓ Booking status updated to "Cancelled"
```

## 📁 Project Structure

```
alx_travel_app/
│
├── alx_travel_app/
│   ├── __init__.py
│   ├── settings.py          # Django settings with env variables
│   ├── urls.py              # Root URL configuration
│   ├── celery.py            # Celery configuration
│   └── wsgi.py
│
├── listings/
│   ├── __init__.py
│   ├── models.py            # Payment, Booking, Listing models
│   ├── views.py             # Payment API endpoints
│   ├── serializers.py       # DRF serializers
│   ├── urls.py              # Listings & Payment routes
│   ├── chapa.py             # Chapa API integration
│   ├── tasks.py             # Celery tasks for email
│   └── management/
│       └── commands/
│           └── seed.py      # Database seeding
│
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

## 🔐 Security Considerations

- ✅ API keys stored in environment variables
- ✅ Never commit `.env` file to version control
- ✅ Use HTTPS in production
- ✅ Implement proper authentication/authorization
- ✅ Validate all payment data before processing
- ✅ Log all transactions for audit purposes

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid API Key" Error**

   - Verify your Chapa API keys in `.env`
   - Ensure no extra spaces in environment variables
   - Check if using correct sandbox/production keys

2. **"Connection Refused" Error**

   - Ensure Redis server is running for Celery
   - Check if port 6379 is available

3. **"Email Not Sending"**

   - Verify email configuration in `.env`
   - Check Celery worker is running
   - Review Celery logs for errors

4. **"Payment Verification Failed"**
   - Check Chapa transaction status manually
   - Verify transaction reference is correct
   - Ensure sufficient time has passed for payment processing

## 📚 Documentation

- [Chapa API Documentation](https://developer.chapa.co/docs)
- [Django Documentation](https://docs.djangoproject.com/)
- [Celery Documentation](https://docs.celeryproject.org/)

## 👤 Author

**Fredrick Mbithi**

## 📄 License

This project is part of the ALX Software Engineering Program.

---

**Note**: This is a development/educational project. For production use, implement additional security measures, comprehensive error handling, and proper testing coverage.
