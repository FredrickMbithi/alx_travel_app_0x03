# API Testing Guide - Chapa Payment Integration

This guide provides step-by-step instructions for testing the Chapa payment integration.

## Prerequisites

Before testing, ensure:

1. Django server is running: `python manage.py runserver`
2. Redis server is running (for Celery)
3. Celery worker is running: `celery -A alx_travel_app worker --loglevel=info`
4. Chapa API credentials are configured in `.env`

## Testing Tools

You can use any of these tools:

- **Postman** (Recommended)
- **cURL**
- **HTTPie**
- **Thunder Client** (VS Code extension)

## Test Scenarios

### 1. Create a Test Booking (Optional)

First, create a booking to associate with a payment:

**Endpoint:** `POST http://localhost:8000/api/bookings/`

**Request Body:**

```json
{
  "user": 1,
  "listing": "listing-uuid-here",
  "start_date": "2024-12-01",
  "end_date": "2024-12-05",
  "status": "Pending"
}
```

**Expected Response:** 201 Created

```json
{
  "id": "uuid-of-booking",
  "user": 1,
  "listing": "listing-uuid-here",
  "start_date": "2024-12-01",
  "end_date": "2024-12-05",
  "status": "Pending",
  "total_price": "6000.00",
  "created_at": "2024-10-19T12:00:00Z"
}
```

---

### 2. Initiate Payment (SUCCESS SCENARIO)

**Endpoint:** `POST http://localhost:8000/api/payments/initiate-payment/`

**Headers:**

```
Content-Type: application/json
```

**Request Body:**

```json
{
  "booking_id": "uuid-from-step-1-or-null",
  "amount": 1500.0,
  "email": "testuser@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "callback_url": "http://localhost:8000/api/payments/callback",
  "return_url": "http://localhost:8000/api/payments/success",
  "currency": "ETB"
}
```

**Expected Response:** 200 OK

```json
{
  "status": "success",
  "message": "Payment initiated successfully",
  "data": {
    "checkout_url": "https://checkout.chapa.co/checkout/web/payment/...",
    "transaction_reference": "TX-ABCD12345678",
    "payment_id": "payment-uuid"
  }
}
```

**What to Check:**

- ✅ Status is "success"
- ✅ checkout_url is returned
- ✅ transaction_reference is generated
- ✅ Payment record created in database with status "Pending"

**cURL Command:**

```bash
curl -X POST http://localhost:8000/api/payments/initiate-payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500.00,
    "email": "testuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "callback_url": "http://localhost:8000/api/payments/callback",
    "return_url": "http://localhost:8000/api/payments/success",
    "currency": "ETB"
  }'
```

---

### 3. Simulate Payment Completion

In a real scenario, the user would:

1. Be redirected to the Chapa checkout URL
2. Enter payment details
3. Complete the payment
4. Be redirected back to your return_url

For testing with Chapa sandbox:

- Use test card details provided in Chapa documentation
- Complete the payment flow

---

### 4. Verify Payment (SUCCESS SCENARIO)

After payment completion, verify the transaction:

**Endpoint:** `GET http://localhost:8000/api/payments/verify-payment/TX-ABCD12345678/`

**Expected Response:** 200 OK

```json
{
  "status": "success",
  "message": "Payment verified successfully",
  "data": {
    "transaction_reference": "TX-ABCD12345678",
    "status": "Completed",
    "amount": 1500.0,
    "email": "testuser@example.com",
    "paid_at": "2024-10-19T12:30:00Z"
  }
}
```

**What to Check:**

- ✅ Status is "Completed"
- ✅ Payment record updated in database
- ✅ Booking status updated to "Confirmed" (if booking exists)
- ✅ Confirmation email queued in Celery
- ✅ Check Celery logs for email task execution

**cURL Command:**

```bash
curl -X GET http://localhost:8000/api/payments/verify-payment/TX-ABCD12345678/
```

---

### 5. Check Payment Status

Get the current status of any payment:

**Endpoint:** `GET http://localhost:8000/api/payments/status/TX-ABCD12345678/`

**Expected Response:** 200 OK

```json
{
  "status": "success",
  "data": {
    "id": "payment-uuid",
    "booking_reference": "TX-ABCD12345678",
    "transaction_id": "chapa-transaction-id",
    "amount": "1500.00",
    "currency": "ETB",
    "email": "testuser@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "status": "Completed",
    "payment_method": "card",
    "paid_at": "2024-10-19T12:30:00Z",
    "created_at": "2024-10-19T12:00:00Z",
    "updated_at": "2024-10-19T12:30:00Z"
  }
}
```

---

### 6. Test Payment Failure Scenario

**Step 1: Initiate Payment**
Same as scenario #2

**Step 2: Use Declined Test Card**
In Chapa sandbox, use a test card that will be declined

**Step 3: Verify Payment**
Call verify endpoint - should return:

```json
{
  "status": "failed",
  "message": "Payment verification failed",
  "data": {
    "transaction_reference": "TX-ABCD12345678",
    "status": "Failed"
  }
}
```

**What to Check:**

- ✅ Status is "Failed"
- ✅ Payment record updated in database
- ✅ Booking status updated to "Cancelled" (if booking exists)

---

### 7. List All Payments

View all payment records:

**Endpoint:** `GET http://localhost:8000/api/payments/`

**Query Parameters (Optional):**

- `status=Completed` - Filter by status
- `ordering=-created_at` - Order by creation date

**Expected Response:** 200 OK

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "payment-uuid",
      "booking_reference": "TX-ABCD12345678",
      "amount": "1500.00",
      "status": "Completed",
      ...
    }
  ]
}
```

---

## Database Verification

After each test, verify the database state:

```bash
python manage.py shell
```

```python
from listings.models import Payment, Booking

# Check payment status
payment = Payment.objects.get(booking_reference='TX-ABCD12345678')
print(f"Status: {payment.status}")
print(f"Amount: {payment.amount}")
print(f"Email: {payment.email}")

# Check booking status (if booking exists)
if payment.booking:
    print(f"Booking Status: {payment.booking.status}")
```

---

## Celery Task Verification

Check if email tasks are being processed:

1. **Check Celery Worker Logs:**
   Look for messages like:

   ```
   [INFO] Task listings.tasks.send_payment_confirmation_email succeeded
   ```

2. **Check Console for Emails (Development):**
   If using console email backend, emails will print in Django console

3. **Manually Test Email Task:**

   ```bash
   python manage.py shell
   ```

   ```python
   from listings.tasks import send_payment_confirmation_email

   result = send_payment_confirmation_email.delay(
       email='test@example.com',
       first_name='John',
       amount=1500.00,
       transaction_reference='TX-TEST123'
   )

   print(result.get())  # Wait for result
   ```

---

## Error Testing

### Test Invalid Data

**1. Invalid Amount:**

```json
{
  "amount": -100,
  "email": "test@example.com",
  ...
}
```

**Expected:** 400 Bad Request with validation error

**2. Missing Required Fields:**

```json
{
  "amount": 1500.0
  // Missing email, first_name, etc.
}
```

**Expected:** 400 Bad Request with validation error

**3. Invalid Email:**

```json
{
  "amount": 1500.00,
  "email": "not-an-email",
  ...
}
```

**Expected:** 400 Bad Request with validation error

**4. Non-existent Transaction:**

```
GET /api/payments/verify-payment/TX-NONEXISTENT/
```

**Expected:** 404 Not Found

---

## Performance Testing

Test with multiple concurrent requests:

```bash
# Using Apache Bench
ab -n 100 -c 10 -T "application/json" -p payment.json \
   http://localhost:8000/api/payments/initiate-payment/
```

---

## Test Results Documentation

Document your test results in this format:

### Payment Initiation Test

```
Date: 2024-10-19
Environment: Development (Sandbox)
Status: ✅ PASSED

Request:
POST /api/payments/initiate-payment/
Body: { amount: 1500.00, email: "test@example.com", ... }

Response:
Status: 200 OK
Time: 1.2s
Body: { status: "success", ... }

Database:
✅ Payment record created
✅ Status: Pending
✅ Transaction reference generated

Logs:
✅ No errors in application logs
✅ Chapa API call successful
```

---

## Troubleshooting

### Common Issues

1. **"Invalid API Key" Error**

   - Check `.env` file has correct Chapa keys
   - Verify no extra spaces in environment variables

2. **"Connection Refused" to Redis**

   - Start Redis: `redis-server`
   - Check Redis is running: `redis-cli ping`

3. **Emails Not Sending**

   - Check Celery worker is running
   - Verify email settings in `.env`
   - Check Celery logs for errors

4. **Import Errors**
   - Run: `pip install -r requirements.txt`
   - Verify all dependencies installed

---

## Next Steps

After successful testing:

1. Document all test results with screenshots
2. Test edge cases and error scenarios
3. Perform load testing
4. Update security configurations for production
5. Set up monitoring and logging
6. Configure production email service
7. Update Chapa credentials to production keys

---

## Sample Test Report Template

```markdown
## Test Report - Chapa Payment Integration

**Date:** October 19, 2024
**Tester:** Your Name
**Environment:** Development/Sandbox

### Test Case 1: Payment Initiation

- Status: ✅ PASSED / ❌ FAILED
- Response Time: 1.2s
- Notes: Payment initiated successfully, checkout URL returned

### Test Case 2: Payment Verification (Success)

- Status: ✅ PASSED / ❌ FAILED
- Response Time: 0.8s
- Notes: Payment verified, status updated to Completed

### Test Case 3: Payment Verification (Failure)

- Status: ✅ PASSED / ❌ FAILED
- Response Time: 0.7s
- Notes: Payment marked as Failed, booking cancelled

### Test Case 4: Email Notification

- Status: ✅ PASSED / ❌ FAILED
- Notes: Confirmation email sent successfully via Celery

### Issues Found:

- None

### Recommendations:

- Add rate limiting for payment endpoints
- Implement webhook for real-time payment updates
```
