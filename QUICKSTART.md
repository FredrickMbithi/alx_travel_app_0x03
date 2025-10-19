# 🚀 Quick Start Guide - Chapa Payment Integration

Get the project running in 5 minutes!

## Prerequisites

- Python 3.8+
- Redis (for Celery)
- Git

## Step 1: Clone & Navigate

```bash
cd alx_travel_app
```

## Step 2: Create Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Environment

Edit `.env` file and add your Chapa credentials:

```env
CHAPA_SECRET_KEY=your_actual_secret_key_here
CHAPA_PUBLIC_KEY=your_actual_public_key_here
```

Get your keys from: https://developer.chapa.co/

## Step 5: Setup Database

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## Step 6: Start Services

Open 3 terminal windows:

**Terminal 1 - Django Server:**

```bash
python manage.py runserver
```

**Terminal 2 - Redis (if not running as service):**

```bash
redis-server
```

**Terminal 3 - Celery Worker:**

```bash
celery -A alx_travel_app worker --loglevel=info
```

## Step 7: Test the API

Open Postman or use cURL:

```bash
curl -X POST http://localhost:8000/api/payments/initiate-payment/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "callback_url": "http://localhost:8000/callback",
    "return_url": "http://localhost:8000/success",
    "currency": "ETB"
  }'
```

## ✅ Success!

If you see a response with a `checkout_url`, you're all set! 🎉

## 📚 Next Steps

- Read `README.md` for full documentation
- Check `API_TESTING_GUIDE.md` for testing scenarios
- Access Django Admin at: http://localhost:8000/admin/

## 🆘 Troubleshooting

### Redis Connection Error

```bash
# Install Redis on Windows via WSL or download from:
# https://github.com/microsoftarchive/redis/releases

# Or use Docker:
docker run -d -p 6379:6379 redis
```

### Import Errors

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Database Errors

```bash
# Delete db.sqlite3 and retry
rm db.sqlite3
python manage.py migrate
```

## 📖 Documentation

- **Full Setup:** `README.md`
- **API Testing:** `API_TESTING_GUIDE.md`
- **Project Summary:** `SETUP_COMPLETE.md`

---

**Need help?** Check the documentation files or review the inline code comments.
