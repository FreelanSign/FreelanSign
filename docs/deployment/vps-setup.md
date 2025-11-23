# VPS Setup Guide - Scaleway VPS-START-S

Scaleway-optimized setup for 2GB RAM VPS (VPS-START-S)

## 1. Provision Scaleway VPS

1. Go to [Scaleway Console](https://console.scaleway.com)
2. Create Instance > VPS-START-S:
   - **RAM**: 2GB
   - **CPU**: 1 vCPU
   - **Storage**: 40GB NVMe
   - **OS**: Ubuntu 22.04 LTS
   - **Region**: Choose closest to your users
3. Note down: IP address, root password

## 2. Initial Server Access

```bash
ssh root@your-server-ip
```

Update system:
```bash
apt update && apt upgrade -y
```

## 3. SWAP Activation (Critical for 2GB RAM)

Create 2GB swap file:
```bash
# Create swap file
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Verify
free -h
```

Tune swap behavior:
```bash
echo 'vm.swappiness=10' >> /etc/sysctl.conf
echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
sysctl -p
```

## 4. Server Hardening

### Create non-root user
```bash
adduser deploy
usermod -aG sudo deploy
```

### SSH Key Authentication
On local machine:
```bash
ssh-copy-id deploy@your-server-ip
```

On server, disable password auth:
```bash
nano /etc/ssh/sshd_config
```

Set:
```
PermitRootLogin no
PasswordAuthentication no
```

Restart SSH:
```bash
systemctl restart sshd
```

### Firewall (UFW)
```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable # N'active jamais UFW (ufw enable) avant d'avoir testé ta connexion SSH dans un deuxième terminal ouvert en parallèle.
```

## 5. Docker Installation

```bash
# Remove old versions
apt remove docker docker-engine docker.io containerd runc

# Install dependencies
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add deploy user to docker group
usermod -aG docker deploy

# Enable Docker service
systemctl enable docker
systemctl start docker

# Verify
docker --version
docker compose version
```

## 6. DNS Configuration

At your DNS provider (e.g., Cloudflare, Namecheap):

### A Records
```
Type: A
Name: @
Value: your-server-ip
TTL: Auto

Type: A
Name: www
Value: your-server-ip
TTL: Auto
```

Verify DNS propagation:
```bash
dig your-domain.com
dig www.your-domain.com
```

Wait 5-30 minutes for DNS to propagate globally.

## 7. SSL Certificate (Certbot + Let's Encrypt)

### Initial setup (HTTP-only mode first)

1. Create temporary nginx config:
```bash
mkdir -p /tmp/certbot-www
```

2. Run temporary nginx for verification:
```bash
docker run -d --name nginx-temp -p 80:80 -v /tmp/certbot-www:/var/www/certbot nginx:alpine
```

3. Obtain certificate:
```bash
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /tmp/certbot-www:/var/www/certbot \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@domain.com \
  --agree-tos \
  --no-eff-email \
  -d your-domain.com \
  -d www.your-domain.com
```

4. Stop temporary nginx:
```bash
docker stop nginx-temp && docker rm nginx-temp
```

5. Update nginx.conf SSL paths:
```nginx
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

### Auto-renewal

Certbot auto-renewal is configured in `docker-compose.certbot.yml` (renews every 12h).

Test renewal:
```bash
docker run --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /tmp/certbot-www:/var/www/certbot \
  certbot/certbot renew --dry-run
```

## 8. Storage Management

### Monitor disk usage
```bash
df -h
docker system df
```

### Cleanup commands

Prune images older than 7 days:
```bash
docker system prune -a --filter "until=168h" -f
```

Remove stopped containers:
```bash
docker container prune -f
```

Remove unused volumes:
```bash
docker volume prune -f
```

### Automated cleanup (cron)

Create cleanup script:
```bash
cat > /usr/local/bin/docker-cleanup.sh << 'EOF'
#!/bin/bash
echo "$(date): Starting Docker cleanup"
docker system prune -a --filter "until=168h" -f
docker volume prune -f
echo "$(date): Cleanup complete"
EOF

chmod +x /usr/local/bin/docker-cleanup.sh
```

Add to cron (weekly on Sunday 3am):
```bash
crontab -e
```

Add line:
```
0 3 * * 0 /usr/local/bin/docker-cleanup.sh >> /var/log/docker-cleanup.log 2>&1
```

## 9. Application Deployment

Clone repository:
```bash
cd /home/deploy
git clone https://github.com/your-username/FreelanSign.git
cd FreelanSign
```

Create `.env` file (see Environment Config Guide).

Start application:
```bash
docker compose -f docker-compose.prod.yml -f docker-compose.certbot.yml up -d
```

Check logs:
```bash
docker compose -f docker-compose.prod.yml logs -f
```

## 10. Verification

### Test HTTP → HTTPS redirect
```bash
curl -I http://your-domain.com
# Should return: HTTP/1.1 301 Moved Permanently
```

### Test HTTPS
```bash
curl -I https://your-domain.com
# Should return: HTTP/2 200
```

### Test API
```bash
curl https://your-domain.com/api/
```

### Check resource usage
```bash
free -h
docker stats --no-stream
```

## Maintenance

### View logs
```bash
# All services
docker compose -f docker-compose.prod.yml logs -f

# Specific service
docker compose -f docker-compose.prod.yml logs -f backend
```

### Restart services
```bash
docker compose -f docker-compose.prod.yml restart
```

### Update application
```bash
cd /home/deploy/FreelanSign
git pull
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### Monitor disk space
```bash
watch -n 60 'df -h && echo && docker system df'
```

## Troubleshooting

### Out of memory
```bash
# Check swap
free -h

# Check memory hogs
docker stats --no-stream

# Restart heavy services
docker compose -f docker-compose.prod.yml restart backend
```

### Certificate issues
```bash
# Check certificate expiry
docker run --rm -v /etc/letsencrypt:/etc/letsencrypt certbot/certbot certificates

# Force renewal
docker compose -f docker-compose.prod.yml -f docker-compose.certbot.yml down
docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v /tmp/certbot-www:/var/www/certbot certbot/certbot renew --force-renewal
docker compose -f docker-compose.prod.yml -f docker-compose.certbot.yml up -d
```

### Disk full
```bash
# Emergency cleanup
docker system prune -a -f --volumes
apt autoremove -y
apt clean
```

## Security Checklist

- [ ] SWAP enabled and configured
- [ ] Firewall (UFW) active with only necessary ports
- [ ] SSH password auth disabled
- [ ] Root login disabled
- [ ] Non-root user created
- [ ] SSL/TLS certificates valid
- [ ] Docker running as non-root user
- [ ] Automatic security updates enabled
- [ ] Monitoring configured (Sentry, UptimeRobot)
- [ ] Backups automated

## Resources

- [Scaleway Documentation](https://www.scaleway.com/en/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
