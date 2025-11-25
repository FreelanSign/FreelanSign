# FreelanSign Master Deployment Guide

This comprehensive guide covers the entire process of deploying FreelanSign to a production environment (Scaleway VPS) using Docker, GitHub Container Registry (GHCR), and Nginx.

> [!IMPORTANT]
> **User Action Required**: Steps marked with 🛑 require your specific input (passwords, API keys, DNS settings). Do not skip these.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Phase 1: Local Preparation](#phase-1-local-preparation)
3. [Phase 2: VPS Provisioning & Hardening](#phase-2-vps-provisioning--hardening)
4. [Phase 3: Server Configuration](#phase-3-server-configuration)
5. [Phase 4: Application Deployment](#phase-4-application-deployment)
6. [Phase 5: Post-Deployment Setup](#phase-5-post-deployment-setup)
7. [Phase 6: Maintenance & Troubleshooting](#phase-6-maintenance--troubleshooting)

---

## 1. Prerequisites

Before starting, ensure you have:

- **Scaleway Account**: For hosting the VPS.
- **Domain Name**: Purchased from a registrar (e.g., Namecheap, Cloudflare).
- **GitHub Account**: With access to the FreelanSign repository.
- **Brevo Account**: For transactional emails (SMTP).
- **Sentry Account**: For error tracking.
- **Local Tools**: Docker, Git, SSH client installed on your machine.

---

## Phase 1: Local Preparation

We use a "Build Local, Deploy Remote" strategy to save VPS resources.

### 1.1. Configure GitHub Container Registry (GHCR)

🛑 **ACTION**: Generate a Personal Access Token (PAT) on GitHub.
1. Go to **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
2. Generate new token with scopes: `write:packages`, `read:packages`, `delete:packages`.
3. **Copy this token**. You will not see it again.

**Login to GHCR locally:**
```bash
export CR_PAT=YOUR_GENERATED_TOKEN
echo $CR_PAT | docker login ghcr.io -u Bertrand2808 --password-stdin
```

### 1.2. Build and Push Docker Images

Run these commands on your **local machine**:

```bash
# Set variables
export GITHUB_ORG=freelansign
export REPO=freelansign
export VERSION=latest

# 1. Build & Push Backend
cd backend
docker build -t ghcr.io/$GITHUB_ORG/$REPO-backend:$VERSION .
docker push ghcr.io/$GITHUB_ORG/$REPO-backend:$VERSION
cd ..

# 2. Build & Push Frontend
cd frontend
docker build --target production-server -t ghcr.io/$GITHUB_ORG/$REPO-frontend:$VERSION .
docker push ghcr.io/$GITHUB_ORG/$REPO-frontend:$VERSION
cd ..
```

---

## Phase 2: VPS Provisioning & Hardening

### 2.1. Provision VPS

🛑 **ACTION**: Create Instance on Scaleway.
1. **Image**: Ubuntu 22.04 LTS (Jammy Jellyfish).
2. **Type**: **VPS-START-S** (2GB RAM, 1 vCPU) - *Minimum required*.
3. **Region**: Choose closest to your users (e.g., Paris, Amsterdam).
4. **SSH Keys**: Add your local public key (`~/.ssh/id_rsa.pub`).

**Note the IP Address**: `YOUR_SERVER_IP`

### 2.2. Initial Access & Updates

SSH into your new server:
```bash
ssh root@YOUR_SERVER_IP
```

Update system packages:
```bash
apt update && apt upgrade -y
```

### 2.3. Configure SWAP (Critical)

Since the VPS has only 2GB RAM, SWAP is **mandatory** to prevent crashes.

```bash
# Create 2GB swap file
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Optimize swap usage
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
sysctl -p
```

### 2.4. Create Deploy User

Do not run the app as root.

```bash
adduser deploy
# Follow prompts to set a strong password

usermod -aG sudo deploy
```

**Setup SSH for `deploy` user:**
On your **local machine**:
```bash
ssh-copy-id deploy@YOUR_SERVER_IP
```

### 2.5. Security Hardening

Back on the **server (as root)**:

**Configure Firewall (UFW):**
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

**Disable Root Login & Password Auth:**
Edit SSH config: `nano /etc/ssh/sshd_config`
```ssh
PermitRootLogin no
PasswordAuthentication no
```
Restart SSH: `systemctl restart sshd`

### 2.6. Install Docker

```bash
# Remove old versions
apt remove docker docker-engine docker.io containerd runc

# Install dependencies
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker key & repo
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add deploy user to docker group
usermod -aG docker deploy
```

**Logout and log back in as `deploy` user:**
```bash
ssh deploy@YOUR_SERVER_IP
```

---

## Phase 3: Server Configuration

### 3.1. DNS Configuration

🛑 **ACTION**: Go to your Domain Registrar (Namecheap, Cloudflare, etc.).

Add the following **A Records**:
| Type | Host | Value | TTL |
|------|------|-------|-----|
| A | @ | YOUR_SERVER_IP | Auto |
| A | www | YOUR_SERVER_IP | Auto |

Verify propagation (can take minutes to hours):
```bash
dig your-domain.com +short
```

### 3.2. Clone Repository

```bash
cd /home/deploy
git clone https://github.com/your-username/FreelanSign.git
cd FreelanSign
```

### 3.3. Configure Environment Variables

🛑 **ACTION**: Create and edit the production `.env` file.

```bash
cp .env.example .env
nano .env
```

**Critical Values to Change:**

1.  **Django Core**:
    *   `SECRET_KEY`: Generate a new random string (50+ chars).
    *   `DEBUG`: Set to `False`.
    *   `ALLOWED_HOSTS`: `your-domain.com,www.your-domain.com,YOUR_SERVER_IP`

2.  **Database**:
    *   `DATABASE_PASSWORD`: Generate a strong password.
    *   `DATABASE_HOST`: `postgres` (internal docker name).

3.  **Email (Brevo)**:
    *   `EMAIL_HOST_PASSWORD`: Your Brevo SMTP Key.
    *   `EMAIL_FROM`: `noreply@your-domain.com`.

4.  **Sentry**:
    *   `SENTRY_DSN`: Your project DSN from Sentry.io.

5.  **Security**:
    *   `SECURE_SSL_REDIRECT`: `True` (after SSL is working).

### 3.4. SSL Certificate Setup (Certbot)

We use a temporary Nginx container to get the initial certificate.

1.  **Create temp directory**:
    ```bash
    mkdir -p /tmp/certbot-www
    ```

2.  **Run temp Nginx**:
    ```bash
    docker run -d --name nginx-temp -p 80:80 -v /tmp/certbot-www:/var/www/certbot nginx:alpine
    ```

3.  **Request Certificate**:
    🛑 **Replace email and domain**:
    ```bash
    docker run -it --rm \
        -v /etc/letsencrypt:/etc/letsencrypt \
        -v /tmp/certbot-www:/var/www/certbot \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email freelansign@gmail.com \
        --agree-tos \
        --no-eff-email \
        -d freelansign.fr \
        -d www.freelansign.fr \
        -d app.freelansign.fr
    ```

**En sortie :**

```bash
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Requesting a certificate for freelansign.fr and 2 more domains

Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/freelansign.fr/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/freelansign.fr/privkey.pem
This certificate expires on 2026-02-21.
These files will be updated when the certificate renews.

NEXT STEPS:
- The certificate will need to be renewed before it expires. Certbot can automatically renew the certificate in the background, but you may need to take steps to enable that functionality. See https://certbot.org/renewal-setup for instructions.

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
If you like Certbot, please consider supporting our work by:
 * Donating to ISRG / Let's Encrypt:   https://letsencrypt.org/donate
 * Donating to EFF:                    https://eff.org/donate-le
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```

4.  **Cleanup**:
    ```bash
    docker stop nginx-temp && docker rm nginx-temp
    ```

---

## Phase 4: Application Deployment

### 4.1. Login to GHCR on VPS

```bash
# Use the same PAT you generated earlier
echo $CR_PAT | docker login ghcr.io -u Bertrand2808 --password-stdin
```

### 4.2. Update Docker Compose

Edit `docker-compose.prod.yml` to point to your GHCR images if not already set:

```yaml
services:
  backend:
    image: ghcr.io/freelansign/freelansign-backend:latest
    # ...
  frontend:
    image: ghcr.io/freelansign/freelansign-frontend:latest
    # ...
```

### 4.3. Start Services

```bash
# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Start containers (including Certbot for auto-renewal)
docker compose -f docker-compose.prod.yml -f docker-compose.certbot.yml up -d
```

### 4.4. Verify Deployment

1.  **Check Containers**:
    ```bash
    docker compose -f docker-compose.prod.yml ps
    ```
    *All services (backend, frontend, postgres, nginx) should be `Up`.*

2.  **Check Logs**:
    ```bash
    docker compose -f docker-compose.prod.yml logs -f
    ```

3.  **Visit Website**:
    Open `https://freelansign.fr`. You should see the application.

---

## Phase 5: Post-Deployment Setup

### 5.1. Automated Backups

1.  **Prepare Scripts**:
    ```bash
    chmod +x scripts/backup.sh scripts/restore.sh
    mkdir -p /home/deploy/backups/{daily,weekly,monthly}
    ```

2.  **Setup Cron Job**:
    ```bash
    crontab -e
    ```
    Add line for daily backup at 3 AM:
    ```cron
    0 3 * * * /home/deploy/FreelanSign/scripts/backup.sh >> /var/log/freelansign-backup.log 2>&1
    ```

### 5.2. Monitoring

1.  **UptimeRobot**:
    *   Create an HTTP monitor for `https://freelansign.fr`.
    *   Create a keyword monitor for `https://freelansign.fr/api/health/` (expect "healthy").

2.  **Sentry**:
    *   Verify you are receiving errors by testing:
        ```bash
        docker compose -f docker-compose.prod.yml exec backend python manage.py shell
        >>> import sentry_sdk
        >>> sentry_sdk.capture_message("Production Test")
        ```

### 5.3. Log Rotation

Ensure `logrotate` is configured to prevent logs from filling the disk.
(See `docs/deployment/monitoring.md` for details).

---

## Phase 6: Maintenance & Troubleshooting

### Common Commands

| Action | Command |
|--------|---------|
| **View Logs** | `docker compose -f docker-compose.prod.yml logs -f [service]` |
| **Restart App** | `docker compose -f docker-compose.prod.yml restart` |
| **Update App** | `git pull && docker compose -f docker-compose.prod.yml pull && docker compose -f docker-compose.prod.yml up -d` |
| **Check Disk** | `df -h` |
| **Check RAM** | `free -h` |

### Troubleshooting Scenarios

**1. "502 Bad Gateway"**
*   **Cause**: Backend container is down or starting up.
*   **Fix**: Check backend logs: `docker compose -f docker-compose.prod.yml logs backend`.

**2. "Database connection failed"**
*   **Cause**: Incorrect credentials in `.env` or Postgres container down.
*   **Fix**: Verify `.env` matches `docker-compose.prod.yml` DB settings.

**3. Disk Full**
*   **Cause**: Docker images or logs piling up.
*   **Fix**: Run cleanup:
    ```bash
    docker system prune -a --filter "until=168h" -f
    ```

**4. SSL Certificate Expired**
*   **Cause**: Auto-renewal failed.
*   **Fix**: Force renewal:
    ```bash
    docker compose -f docker-compose.prod.yml -f docker-compose.certbot.yml run --rm certbot renew --force-renewal
    docker compose -f docker-compose.prod.yml restart nginx
    ```

---

## Emergency Rollback

If a deployment fails, roll back to the previous version:

1.  **Pull previous tag**:
    ```bash
    docker pull ghcr.io/user/repo-backend:PREVIOUS_VERSION
    ```
2.  **Update Compose**: Point `docker-compose.prod.yml` to that version.
3.  **Redeploy**:
    ```bash
    docker compose -f docker-compose.prod.yml up -d
    ```
