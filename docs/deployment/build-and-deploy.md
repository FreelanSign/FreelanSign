# Build & Deploy Workflow - GitHub Container Registry

Strategy: Build images locally → Push to GHCR → Pull on VPS (saves VPS resources)

## Why Build Locally?

Scaleway 2GB VPS constraints:
- Limited RAM for building (frontend Node build needs 1GB+)
- Limited storage (build artifacts consume space)
- Slower CPU (build takes 10-15min vs 2-3min locally)

**Solution**: Build on powerful local machine, push to registry, pull on VPS.

## Prerequisites

- Docker installed locally
- GitHub account with repo access
- GitHub Personal Access Token (PAT) with `write:packages` scope

## 1. GitHub Container Registry Setup

### Create Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with scopes:
   - `write:packages` (upload images)
   - `read:packages` (pull images)
   - `delete:packages` (optional cleanup)
3. Copy token (shown once only)

### Login to GHCR (Local)

```bash
export GITHUB_TOKEN=your_token_here
echo $GITHUB_TOKEN | docker login ghcr.io -u your-github-username --password-stdin
```

Store credentials:
```bash
# Add to ~/.bashrc or ~/.zshrc
export GHCR_USERNAME=your-github-username
export GHCR_TOKEN=your_token_here
```

## 2. Build Images Locally

### Set variables
```bash
export GITHUB_USERNAME=your-github-username
export VERSION=v0.3.0  # or use git tag
export REPO=freelansign
```

### Build backend
```bash
cd backend
docker build -t ghcr.io/$GITHUB_USERNAME/$REPO-backend:$VERSION .
docker build -t ghcr.io/$GITHUB_USERNAME/$REPO-backend:latest .
cd ..
```

### Build frontend
```bash
cd frontend
docker build --target production-server -t ghcr.io/$GITHUB_USERNAME/$REPO-frontend:$VERSION .
docker build --target production-server -t ghcr.io/$GITHUB_USERNAME/$REPO-frontend:latest .
cd ..
```

### Verify images
```bash
docker images | grep $REPO
```

## 3. Push to GHCR

```bash
# Push backend
docker push ghcr.io/$GITHUB_USERNAME/$REPO-backend:$VERSION
docker push ghcr.io/$GITHUB_USERNAME/$REPO-backend:latest

# Push frontend
docker push ghcr.io/$GITHUB_USERNAME/$REPO-frontend:$VERSION
docker push ghcr.io/$GITHUB_USERNAME/$REPO-frontend:latest
```

Verify on GitHub:
```
https://github.com/your-username?tab=packages
```

## 4. Deploy on VPS

### Login to GHCR (VPS)

SSH to VPS:
```bash
ssh deploy@your-server-ip
```

Login to registry:
```bash
echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USERNAME --password-stdin
```

### Update docker-compose.prod.yml

Edit `docker-compose.prod.yml`:
```yaml
services:
  backend:
    image: ghcr.io/your-username/freelansign-backend:latest
    # Remove build section
    # build:
    #   context: ./backend
    #   dockerfile: Dockerfile

  frontend:
    image: ghcr.io/your-username/freelansign-frontend:latest
    # Remove build section
```

### Pull and deploy

```bash
cd /home/deploy/FreelanSign

# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Stop old containers
docker compose -f docker-compose.prod.yml down

# Start with new images
docker compose -f docker-compose.prod.yml -f docker-compose.certbot.yml up -d

# Verify
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

## 5. Storage Management on VPS

### Monitor disk usage
```bash
df -h
docker system df
```

### Cleanup old images (168h = 7 days)
```bash
docker system prune -a --filter "until=168h" -f
```

### Remove specific old images
```bash
# List all images
docker images

# Remove old tags
docker rmi ghcr.io/username/freelansign-backend:v0.2.0
docker rmi ghcr.io/username/freelansign-frontend:v0.2.0
```

### Automated cleanup script

Already configured in VPS setup (`/usr/local/bin/docker-cleanup.sh`), runs weekly.

Manual trigger:
```bash
/usr/local/bin/docker-cleanup.sh
```

## 6. CI/CD Automation (Optional)

### GitHub Actions Workflow

Create `.github/workflows/build-deploy.yml`:

```yaml
name: Build and Push to GHCR

on:
  push:
    branches: [main, dev]
    tags: ['v*']

env:
  REGISTRY: ghcr.io
  IMAGE_BACKEND: ghcr.io/${{ github.repository_owner }}/freelansign-backend
  IMAGE_FRONTEND: ghcr.io/${{ github.repository_owner }}/freelansign-frontend

jobs:
  build-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: |
            ${{ env.IMAGE_BACKEND }}
            ${{ env.IMAGE_FRONTEND }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: ${{ env.IMAGE_BACKEND }}:${{ steps.meta.outputs.tags }}
          cache-from: type=registry,ref=${{ env.IMAGE_BACKEND }}:latest
          cache-to: type=inline

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: ./frontend
          target: production-server
          push: true
          tags: ${{ env.IMAGE_FRONTEND }}:${{ steps.meta.outputs.tags }}
          cache-from: type=registry,ref=${{ env.IMAGE_FRONTEND }}:latest
          cache-to: type=inline
```

Push triggers automatic build:
```bash
git tag v0.3.0
git push origin v0.3.0
```

## 7. Deployment Strategies

### Rolling update (zero downtime)

```bash
# Pull new images
docker compose -f docker-compose.prod.yml pull

# Recreate only changed services
docker compose -f docker-compose.prod.yml up -d --no-deps backend
docker compose -f docker-compose.prod.yml up -d --no-deps frontend
```

### Full restart (with downtime)

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml -f docker-compose.certbot.yml up -d
```

### Rollback to previous version

```bash
# Pull specific version
docker pull ghcr.io/$GITHUB_USERNAME/$REPO-backend:v0.2.0
docker pull ghcr.io/$GITHUB_USERNAME/$REPO-frontend:v0.2.0

# Tag as latest
docker tag ghcr.io/$GITHUB_USERNAME/$REPO-backend:v0.2.0 ghcr.io/$GITHUB_USERNAME/$REPO-backend:latest
docker tag ghcr.io/$GITHUB_USERNAME/$REPO-frontend:v0.2.0 ghcr.io/$GITHUB_USERNAME/$REPO-frontend:latest

# Restart
docker compose -f docker-compose.prod.yml up -d
```

## 8. Quick Deploy Script

Create `deploy.sh`:

```bash
#!/bin/bash
set -e

VERSION=${1:-latest}
GITHUB_USERNAME="your-username"
REPO="freelansign"

echo "Building version: $VERSION"

if [[ -n $(git status -s) ]]; then
    echo "⚠️  Attention : Vous avez des fichiers non commités locally."
    read -p "Continuer quand même ? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then exit 1; fi
fi

# Build backend
echo "Building backend..."
cd backend
docker build -t ghcr.io/$GITHUB_USERNAME/$REPO-backend:$VERSION .
docker push ghcr.io/$GITHUB_USERNAME/$REPO-backend:$VERSION

# Build frontend
echo "Building frontend..."
cd ../frontend
docker build --target production-server -t ghcr.io/$GITHUB_USERNAME/$REPO-frontend:$VERSION .
docker push ghcr.io/$GITHUB_USERNAME/$REPO-frontend:$VERSION

echo "✅ Images pushed to GHCR"
echo "Deploy on VPS with:"
echo "  ssh deploy@your-server-ip"
echo "  cd /home/deploy/FreelanSign"
echo "  docker compose -f docker-compose.prod.yml pull"
echo "  docker compose -f docker-compose.prod.yml up -d"
```

Usage:
```bash
chmod +x deploy.sh
./deploy.sh v0.3.0
```

## 9. Verification

After deployment:

```bash
# Check running containers
docker ps

# Check logs
docker compose -f docker-compose.prod.yml logs -f

# Test endpoints
curl -I https://your-domain.com
curl https://your-domain.com/api/

# Monitor resources
docker stats --no-stream
```

## 10. Troubleshooting

### Image pull fails (authentication)
```bash
# Re-login
echo $GHCR_TOKEN | docker login ghcr.io -u $GHCR_USERNAME --password-stdin

# Verify
docker login ghcr.io
```

### Image not found
```bash
# Check package visibility (must be public or you must be authenticated)
# GitHub → Packages → freelansign-backend → Settings → Change visibility
```

### Build fails locally
```bash
# Check Docker daemon
docker info

# Check disk space
df -h

# Clean build cache
docker builder prune -a
```

### VPS disk full
```bash
# Emergency cleanup
docker system prune -a -f --volumes

# Check what's using space
docker system df -v
du -sh /var/lib/docker/*
```

### Container won't start after update
```bash
# Check logs
docker compose -f docker-compose.prod.yml logs backend

# Rollback
docker compose -f docker-compose.prod.yml down
# Change image tags in compose file to previous version
docker compose -f docker-compose.prod.yml up -d
```

## Best Practices

1. **Tag images with versions**: Use semantic versioning (v1.2.3)
2. **Always push `latest` tag**: For easy updates
3. **Test locally first**: Run `docker compose up` before pushing
4. **Backup before deploy**: Snapshot DB before major updates
5. **Monitor disk space**: Run cleanup weekly
6. **Keep credentials secure**: Use secrets, never commit tokens
7. **Document changes**: Update changelog with each release

## Monitoring Deployments

Track deployment history:
```bash
# On VPS
docker ps --format "table {{.Image}}\t{{.Status}}\t{{.Names}}"

# Check image digests
docker images --digests | grep freelansign
```

## Resources

- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Compose Production](https://docs.docker.com/compose/production/)
- [Docker Image Management](https://docs.docker.com/engine/reference/commandline/image/)
