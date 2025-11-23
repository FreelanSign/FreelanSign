# Environment Configuration Guide

Complete guide for configuring FreelanSign production environment variables.

## Overview

Environment variables are stored in `.env` file at repository root. Reference `.env.example` for template.

## Quick Start

```bash
# On VPS
cd /home/deploy/FreelanSign
cp .env.example .env
nano .env  # Edit with your values
```

## Required Variables

### Django Core

#### SECRET_KEY
Django secret key for cryptographic signing.

**Generate**:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Example**:
```env
SECRET_KEY=django-insecure-9k#2$x@4h7!m&p*q3w8e+r5t6y7u8i9o0p-a_s^d%f(g)h
```

**Security**: Never commit to git, rotate regularly.

#### DEBUG
Debug mode (MUST be False in production).

```env
DEBUG=False
```

**Warning**: `DEBUG=True` exposes sensitive data in error pages.

#### ALLOWED_HOSTS
Comma-separated list of domains that can serve the app.

```env
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

**Example**:
```env
ALLOWED_HOSTS=freelansign.com,www.freelansign.com,api.freelansign.com
```

**Testing**: Include VPS IP for initial setup:
```env
ALLOWED_HOSTS=your-domain.com,123.45.67.89
```

#### LOG_LEVEL
Logging verbosity.

```env
LOG_LEVEL=INFO
```

**Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
**Recommendation**: `INFO` for production, `DEBUG` for troubleshooting.

---

### Database (PostgreSQL)

#### DATABASE_NAME
PostgreSQL database name.

```env
DATABASE_NAME=freelansign
```

#### DATABASE_USER
PostgreSQL username.

```env
DATABASE_USER=fs_user
```

**Security**: Avoid default names like `postgres`, `admin`.

#### DATABASE_PASSWORD
Strong password for database user.

**Generate**:
```bash
openssl rand -base64 32
```

```env
DATABASE_PASSWORD=xK9mL2nP5qR8sT4vW7yZ0aB3cD6eF9gH
```

**Requirements**: 32+ chars, alphanumeric + symbols.

#### DATABASE_HOST
Database host (use service name from docker-compose).

```env
DATABASE_HOST=postgres
```

**Note**: For external DB, use IP/hostname.

#### DATABASE_PORT
PostgreSQL port.

```env
DATABASE_PORT=5432
```

---

### Email (Brevo/Sendinblue)

#### EMAIL_BACKEND
Django email backend (use SMTP for production).

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

#### EMAIL_HOST
SMTP server hostname.

**Brevo**:
```env
EMAIL_HOST=smtp-relay.brevo.com
```

**Other providers**:
- SendGrid: `smtp.sendgrid.net`
- Mailgun: `smtp.mailgun.org`
- AWS SES: `email-smtp.us-east-1.amazonaws.com`

#### EMAIL_PORT
SMTP port.

```env
EMAIL_PORT=587
```

**Ports**:
- `587`: TLS (recommended)
- `465`: SSL
- `25`: Unencrypted (not recommended)

#### EMAIL_USE_TLS
Enable TLS encryption.

```env
EMAIL_USE_TLS=True
```

**Note**: Use `True` for port 587, `False` for port 465 (use SSL instead).

#### EMAIL_USE_SSL
Enable SSL encryption.

```env
EMAIL_USE_SSL=False
```

**Note**: Use `True` for port 465, `False` for port 587 (use TLS instead).

#### EMAIL_HOST_USER
SMTP username/login.

**Brevo**: Your Brevo login email
```env
EMAIL_HOST_USER=your-email@domain.com
```

**SendGrid**: `apikey` (literal string)
**AWS SES**: IAM SMTP username

#### EMAIL_HOST_PASSWORD
SMTP password/API key.

**Brevo**:
1. Go to [Brevo SMTP Settings](https://app.brevo.com/settings/keys/smtp)
2. Copy SMTP Key

```env
EMAIL_HOST_PASSWORD=xkeyab123456789ABCDEF
```

**SendGrid**: API key from dashboard
**AWS SES**: IAM SMTP password

#### EMAIL_FROM
Default sender email address.

```env
EMAIL_FROM=noreply@your-domain.com
```

**Requirements**:
- Must be verified sender in Brevo
- Use subdomain (noreply@, hello@, contact@)
- Match SPF/DKIM records

#### RESET_PASSWORD_URL
Frontend URL for password reset link.

```env
RESET_PASSWORD_URL=https://your-domain.com/reset-password
```

---

### Sentry (Error Tracking)

#### SENTRY_DSN
Sentry Data Source Name (project identifier).

**Get DSN**:
1. Go to [Sentry.io](https://sentry.io)
2. Create project → Django
3. Copy DSN from Settings → Client Keys

```env
SENTRY_DSN=https://abc123def456789@o123456.ingest.sentry.io/987654
```

**Optional**: Leave empty to disable Sentry.

#### SENTRY_ENVIRONMENT
Environment tag for error grouping.

```env
SENTRY_ENVIRONMENT=production
```

**Options**: `production`, `staging`, `development`

#### SENTRY_TRACES_SAMPLE_RATE
Percentage of transactions to monitor (0.0 to 1.0).

```env
SENTRY_TRACES_SAMPLE_RATE=0.1
```

**Recommendations**:
- `0.1` (10%): Production with moderate traffic
- `0.01` (1%): High traffic sites
- `1.0` (100%): Staging/development

**Cost**: Higher rates = more Sentry quota usage.

---

### Django Security (Production)

#### SECURE_SSL_REDIRECT
Force HTTPS redirects.

```env
SECURE_SSL_REDIRECT=True
```

**Note**: Set `False` for initial HTTP-only setup, then `True` after SSL works.

#### SECURE_HSTS_SECONDS
HTTP Strict Transport Security duration (seconds).

```env
SECURE_HSTS_SECONDS=31536000
```

**Values**:
- `31536000` (1 year): Production
- `0`: Disable HSTS (testing only)

**Warning**: Once enabled, browsers cache this. Test thoroughly first.

#### SECURE_HSTS_INCLUDE_SUBDOMAINS
Apply HSTS to all subdomains.

```env
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
```

**Requirement**: All subdomains must support HTTPS.

#### SECURE_HSTS_PRELOAD
Enable HSTS preload list submission.

```env
SECURE_HSTS_PRELOAD=True
```

**Note**: Submit to [hstspreload.org](https://hstspreload.org) after enabling.

#### SESSION_COOKIE_SECURE
Send session cookie only over HTTPS.

```env
SESSION_COOKIE_SECURE=True
```

#### CSRF_COOKIE_SECURE
Send CSRF cookie only over HTTPS.

```env
CSRF_COOKIE_SECURE=True
```

---

### CORS (Cross-Origin Resource Sharing)

#### CORS_ALLOWED_ORIGINS
Comma-separated list of allowed frontend origins.

```env
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

**Security**: List only your actual frontend domains.

---

## Complete Production .env Example

```env
# Django Core
SECRET_KEY=django-insecure-REPLACE-WITH-GENERATED-KEY
DEBUG=False
ALLOWED_HOSTS=freelansign.com,www.freelansign.com
LOG_LEVEL=INFO

# Database
DATABASE_NAME=freelansign
DATABASE_USER=fs_user
DATABASE_PASSWORD=REPLACE-WITH-STRONG-PASSWORD
DATABASE_HOST=postgres
DATABASE_PORT=5432

# Email (Brevo)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=REPLACE-WITH-BREVO-SMTP-KEY
EMAIL_FROM=noreply@freelansign.com
RESET_PASSWORD_URL=https://freelansign.com/reset-password

# Sentry
SENTRY_DSN=https://REPLACE-WITH-SENTRY-DSN@sentry.io/PROJECT-ID
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Django Security
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# CORS
CORS_ALLOWED_ORIGINS=https://freelansign.com,https://www.freelansign.com
```

---

## Development .env Example

```env
# Django Core
SECRET_KEY=django-insecure-dev-key-not-for-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
LOG_LEVEL=DEBUG

# Database (local)
DATABASE_NAME=freelansign_dev
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Email (Mailtrap for testing)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=False
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-mailtrap-user
EMAIL_HOST_PASSWORD=your-mailtrap-password
EMAIL_FROM=noreply@example.com
RESET_PASSWORD_URL=http://localhost:3000/reset-password

# Sentry (disabled in dev)
# SENTRY_DSN=

# Django Security (disabled in dev)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# CORS (permissive in dev)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## Setup Guides

### Brevo (Email)

1. **Sign up**: [Brevo.com](https://www.brevo.com) (free tier: 300 emails/day)
2. **Verify sender**:
   - Settings → Senders → Add Sender
   - Verify email/domain
3. **Get SMTP credentials**:
   - Settings → SMTP & API → SMTP Key
   - Copy key to `EMAIL_HOST_PASSWORD`
4. **Test**:
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Body', 'noreply@yourdomain.com', ['test@example.com'])
   ```

### Sentry

1. **Sign up**: [Sentry.io](https://sentry.io) (free tier: 5k events/month)
2. **Create project**: Django
3. **Copy DSN**: Settings → Client Keys (DSN)
4. **Test**:
   ```bash
   python manage.py shell
   >>> from sentry_sdk import capture_message
   >>> capture_message("Test from Django")
   ```
5. **Verify**: Check Sentry dashboard for event

---

## Validation

### Check all required variables
```bash
# On VPS
cd /home/deploy/FreelanSign
cat .env | grep -E '^(SECRET_KEY|DEBUG|ALLOWED_HOSTS|DATABASE_|EMAIL_|SENTRY_)' | wc -l
# Should show 20+ lines
```

### Test configuration
```bash
docker compose -f docker-compose.prod.yml config
# Should not show errors
```

### Verify Django settings
```bash
docker compose -f docker-compose.prod.yml run --rm backend python manage.py check --deploy
# Should pass all checks
```

---

## Security Checklist

- [ ] `SECRET_KEY` is random and unique (not from tutorial)
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` contains only your domains
- [ ] Database password is 32+ characters
- [ ] `.env` is in `.gitignore` (never committed)
- [ ] Email credentials are from verified sender
- [ ] HTTPS security settings enabled after SSL works
- [ ] CORS origins list only your frontend domains
- [ ] Sentry DSN is from correct project
- [ ] File permissions: `chmod 600 .env` on VPS

---

## Troubleshooting

### Variable not loading
```bash
# Check .env file exists
ls -la /home/deploy/FreelanSign/.env

# Check docker-compose loads it
docker compose -f docker-compose.prod.yml config | grep SECRET_KEY

# Check container sees it
docker compose -f docker-compose.prod.yml exec backend env | grep SECRET_KEY
```

### Email not sending
```bash
# Test SMTP connection
docker compose -f docker-compose.prod.yml exec backend python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@domain.com', ['to@domain.com'])

# Check logs
docker compose -f docker-compose.prod.yml logs backend | grep -i email
```

### Sentry not receiving errors
```bash
# Force test error
docker compose -f docker-compose.prod.yml exec backend python manage.py shell
>>> import sentry_sdk
>>> sentry_sdk.capture_message("Test error")

# Check Sentry dashboard within 1-2 minutes
```

---

## Resources

- [Django Settings Best Practices](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [Brevo SMTP Documentation](https://help.brevo.com/hc/en-us/articles/209465765)
- [Sentry Django Integration](https://docs.sentry.io/platforms/python/guides/django/)
- [12-Factor App Config](https://12factor.net/config)
