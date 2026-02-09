# ButterflyFx - Docker Deployment Guide

**Quick deployment guide for containerized ButterflyFx server**

---

## Quick Start (Local Testing)

### 1. Build and Run with Docker Compose

```bash
# Build and start
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Test API
curl http://localhost:8000/api/v1/health
```

### 2. Access the Server

- **API Base:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc
- **Health Check:** http://localhost:8000/api/v1/health

### 3. Stop the Server

```bash
docker-compose down
```

---

## VPS Deployment (Production)

### Prerequisites

- VPS with Ubuntu 22.04+ (or similar)
- 8GB+ RAM (16GB recommended for 15GB capacity)
- 4+ CPU cores
- SSH access with sudo privileges
- Domain name (optional, for SSL)

### One-Command Deployment

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/kenbin64/dimensionsos/main/deploy.sh -o deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh production
```

**That's it!** The script will:
1. Install Docker and Docker Compose (if needed)
2. Clone the repository from GitHub
3. Build the Docker image
4. Start the server with 17 workers (production config)
5. Run health checks
6. Display status and logs

---

## Manual VPS Deployment

If you prefer manual control:

### 1. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository

```bash
# Create deployment directory
sudo mkdir -p /opt/butterflyfx
cd /opt/butterflyfx

# Clone from GitHub
sudo git clone https://github.com/kenbin64/dimensionsos.git .
```

### 3. Configure Environment

```bash
# Create .env file (optional)
cat > .env << EOF
WORKERS=17
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info
EOF
```

### 4. Build and Deploy

```bash
# Build image
sudo docker-compose build

# Start server
sudo docker-compose up -d

# Check status
sudo docker-compose ps

# View logs
sudo docker-compose logs -f
```

### 5. Verify Deployment

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Metrics
curl http://localhost:8000/api/v1/metrics

# Create test substrate
curl -X POST http://localhost:8000/api/v1/substrates \
  -H "Content-Type: application/json" \
  -d '{"expression_type": "lambda", "expression_code": "lambda **kw: kw.get(\"x\", 0) * 2"}'
```

---

## Configuration

### Environment Variables

Edit `docker-compose.yml` or create `.env` file:

```bash
# Number of worker processes
WORKERS=17              # (CPU cores * 2) + 1

# Server binding
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=info          # debug, info, warning, error

# Python
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '8.0'       # Max CPU cores
      memory: 16G       # Max RAM
    reservations:
      cpus: '4.0'       # Reserved CPU
      memory: 8G        # Reserved RAM
```

---

## Updates and Maintenance

### Update from GitHub

```bash
cd /opt/butterflyfx
sudo git pull origin main
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

Or use the deployment script:

```bash
sudo ./deploy.sh production
```

### View Logs

```bash
# Follow logs
sudo docker-compose logs -f

# Last 100 lines
sudo docker-compose logs --tail=100

# Specific service
sudo docker-compose logs -f butterflyfx
```

### Restart Server

```bash
# Restart all services
sudo docker-compose restart

# Restart specific service
sudo docker-compose restart butterflyfx
```

### Stop Server

```bash
# Stop (keeps containers)
sudo docker-compose stop

# Stop and remove containers
sudo docker-compose down

# Stop and remove everything (including volumes)
sudo docker-compose down -v
```

---

## Monitoring

### Container Status

```bash
# List running containers
sudo docker-compose ps

# Container resource usage
sudo docker stats
```

### Application Metrics

```bash
# Get metrics
curl http://localhost:8000/api/v1/metrics

# Pretty print
curl http://localhost:8000/api/v1/metrics | python -m json.tool
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
sudo docker-compose logs

# Check Docker daemon
sudo systemctl status docker

# Rebuild from scratch
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### Port already in use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8080:8000"  # External:Internal
```

### Out of memory

```bash
# Check memory usage
free -h

# Reduce workers in docker-compose.yml
environment:
  - WORKERS=4

# Restart
sudo docker-compose restart
```

---

## Next Steps

1. ✅ **Deploy to VPS** - Use `deploy.sh` script
2. ✅ **Test API** - Create substrates, test operations
3. ⏭️ **Add SSL** - Use Nginx reverse proxy with Let's Encrypt
4. ⏭️ **Monitor** - Set up logging and metrics collection
5. ⏭️ **Scale** - Add Redis backend for distributed storage

See `DEPLOYMENT_GUIDE.md` for advanced topics (SSL, Nginx, monitoring, scaling).

---

**Your ButterflyFx server is ready to deploy!** 🦋🐳🚀

