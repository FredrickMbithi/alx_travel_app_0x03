# 🚀 Deployment Checklist

Use this checklist before pushing to production.

## Pre-Deployment Checklist

### Security

- [ ] Update `SECRET_KEY` in `.env` with a strong, random value
- [ ] Set `DEBUG=False` in production `.env`
- [ ] Update `ALLOWED_HOSTS` with your domain(s)
- [ ] Verify `.env` is in `.gitignore` (never commit secrets!)
- [ ] Use production Chapa API keys (not sandbox)
- [ ] Enable HTTPS only (no HTTP)
- [ ] Configure CORS for specific domains only
- [ ] Add rate limiting to payment endpoints
- [ ] Enable Django security middleware settings

### Database

- [ ] Migrate from SQLite to PostgreSQL (recommended)
- [ ] Run `python manage.py makemigrations --check`
- [ ] Run `python manage.py migrate`
- [ ] Create database backups schedule
- [ ] Set up database connection pooling

### Email Configuration

- [ ] Configure production email service (SendGrid, Mailgun, AWS SES)
- [ ] Update `EMAIL_BACKEND` in settings
- [ ] Verify email templates
- [ ] Test email delivery
- [ ] Set up SPF, DKIM, DMARC records

### Celery & Redis

- [ ] Use production Redis instance (not localhost)
- [ ] Configure Redis password authentication
- [ ] Set up Redis persistence
- [ ] Configure Celery result backend
- [ ] Set up Celery beat for scheduled tasks
- [ ] Monitor Celery worker health

### Static & Media Files

- [ ] Run `python manage.py collectstatic`
- [ ] Configure S3/CloudFront for static files (optional)
- [ ] Set up media file storage (S3 recommended)
- [ ] Configure proper CORS for media files

### Testing

- [ ] Run all unit tests: `python manage.py test`
- [ ] Test payment initiation flow
- [ ] Test payment verification (success & failure)
- [ ] Test email sending
- [ ] Load test with Apache Bench or Locust
- [ ] Test error handling scenarios
- [ ] Verify Celery tasks execute correctly

### Monitoring & Logging

- [ ] Set up error tracking (Sentry, Rollbar)
- [ ] Configure application logging
- [ ] Set up server monitoring (DataDog, New Relic)
- [ ] Configure uptime monitoring (Pingdom, UptimeRobot)
- [ ] Set up payment transaction logging
- [ ] Configure alerts for failed payments

### Performance

- [ ] Enable Django caching (Redis/Memcached)
- [ ] Add database indexes (already done in models)
- [ ] Enable gzip compression
- [ ] Configure CDN for static files
- [ ] Optimize database queries (use `select_related`)
- [ ] Set up connection pooling

### Documentation

- [ ] Update README with production setup
- [ ] Document API endpoints (Swagger/OpenAPI optional)
- [ ] Create deployment runbook
- [ ] Document backup/restore procedures
- [ ] Create incident response plan

## Production Environment Variables

```env
# Django
SECRET_KEY=<generate-strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Chapa Production Keys
CHAPA_SECRET_KEY=<production-secret-key>
CHAPA_PUBLIC_KEY=<production-public-key>
CHAPA_BASE_URL=https://api.chapa.co/v1

# Email (Production Service)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=<sendgrid-api-key>
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Celery & Redis (Production)
CELERY_BROKER_URL=redis://:password@redis-host:6379/0
CELERY_RESULT_BACKEND=redis://:password@redis-host:6379/0

# Monitoring
SENTRY_DSN=<sentry-dsn-url>
```

## Deployment Platforms

### Option 1: Heroku

```bash
# Install Heroku CLI
heroku login
heroku create alx-travel-app
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
heroku config:set SECRET_KEY=your-secret-key
heroku config:set CHAPA_SECRET_KEY=your-key
git push heroku main
heroku run python manage.py migrate
```

### Option 2: DigitalOcean App Platform

1. Connect GitHub repository
2. Configure environment variables
3. Add PostgreSQL database
4. Add Redis database
5. Deploy

### Option 3: AWS (EC2 + RDS + ElastiCache)

1. Launch EC2 instance (Ubuntu 20.04+)
2. Set up RDS PostgreSQL
3. Set up ElastiCache Redis
4. Configure security groups
5. Install dependencies
6. Use Gunicorn + Nginx
7. Set up supervisor for Celery

### Option 4: Docker

```dockerfile
# Use provided Dockerfile (create if needed)
docker build -t alx-travel-app .
docker-compose up -d
```

## Post-Deployment Verification

- [ ] Access application at production URL
- [ ] Test payment initiation endpoint
- [ ] Complete a test transaction
- [ ] Verify email delivery
- [ ] Check Celery worker logs
- [ ] Monitor error rates
- [ ] Verify database connections
- [ ] Test admin panel access
- [ ] Check SSL certificate

## Rollback Plan

If issues occur:

1. **Database:** Restore from latest backup
2. **Code:** `git revert` or redeploy previous version
3. **Environment:** Verify all config variables
4. **Communication:** Notify users of any downtime

## Maintenance Windows

Schedule regular maintenance:

- Database backups: Daily
- Security updates: Weekly
- Dependency updates: Monthly
- Performance review: Monthly

## Support Contacts

- **DevOps:** [Your DevOps Email]
- **Backend:** [Your Backend Email]
- **Chapa Support:** support@chapa.co
- **On-Call:** [Your On-Call Number]

---

## Production Settings Template

Create `alx_travel_app/settings_production.py`:

```python
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Database - PostgreSQL
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

---

**✅ Once all items are checked, you're ready for production!**
