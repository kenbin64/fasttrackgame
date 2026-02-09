# ButterflyFx Server - Deployment Guide

Quick guide to deploy ButterflyFx server to production.

---

## Quick Deploy (Single Server)

### 1. Server Requirements

**Minimum:**
- Ubuntu 22.04 LTS (or similar)
- 8 GB RAM
- 4 CPU cores
- Python 3.10+

**Recommended (15GB RAM):**
- Ubuntu 22.04 LTS
- 16 GB RAM
- 8 CPU cores
- Python 3.14

### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.14 (if not available, use 3.10+)
sudo apt install python3.14 python3.14-venv python3-pip -y

# Clone repository
git clone https://github.com/kenbin64/butterflyfxpython.git
cd butterflyfxpython

# Create virtual environment
python3.14 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r server/requirements.txt
```

### 3. Run Server

**Development:**
```bash
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

**Production (Single Worker):**
```bash
uvicorn server.main:app --host 0.0.0.0 --port 8000 --log-level warning
```

**Production (Multi-Worker):**
```bash
# Calculate workers: (CPU cores * 2) + 1
# For 8 cores: 17 workers
uvicorn server.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 17 \
  --log-level warning
```

### 4. Test Deployment

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Create substrate
curl -X POST http://localhost:8000/api/v1/substrates \
  -H "Content-Type: application/json" \
  -d '{"expression_type": "lambda", "expression_code": "lambda **kw: kw.get(\"x\", 0) * 2"}'
```

---

## Production Deployment (Systemd Service)

### 1. Create Service File

```bash
sudo nano /etc/systemd/system/butterflyfx.service
```

**Content:**
```ini
[Unit]
Description=ButterflyFx Server
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/butterflyfx
Environment="PATH=/opt/butterflyfx/.venv/bin"
ExecStart=/opt/butterflyfx/.venv/bin/uvicorn server.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 17 \
  --log-level warning
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable butterflyfx

# Start service
sudo systemctl start butterflyfx

# Check status
sudo systemctl status butterflyfx

# View logs
sudo journalctl -u butterflyfx -f
```

---

## Nginx Reverse Proxy (Recommended)

### 1. Install Nginx

```bash
sudo apt install nginx -y
```

### 2. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/butterflyfx
```

**Content:**
```nginx
upstream butterflyfx {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;

    location / {
        proxy_pass http://butterflyfx;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 3. Enable Site

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/butterflyfx /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

---

## SSL/TLS (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

---

## Monitoring

### 1. System Resources

```bash
# Install htop
sudo apt install htop -y

# Monitor in real-time
htop
```

### 2. Application Logs

```bash
# Follow logs
sudo journalctl -u butterflyfx -f

# Last 100 lines
sudo journalctl -u butterflyfx -n 100
```

### 3. API Metrics

```bash
# Check metrics endpoint
curl http://localhost:8000/api/v1/metrics
```

---

## Performance Tuning

### 1. Increase File Descriptors

```bash
# Edit limits
sudo nano /etc/security/limits.conf

# Add:
* soft nofile 65536
* hard nofile 65536
```

### 2. Optimize Kernel

```bash
# Edit sysctl
sudo nano /etc/sysctl.conf

# Add:
net.core.somaxconn = 65536
net.ipv4.tcp_max_syn_backlog = 8192
```

Apply:
```bash
sudo sysctl -p
```

---

## Backup & Recovery

### 1. Backup (In-Memory Registry)

Currently, substrates are in-memory only. For persistence:

```python
# Add to server/main.py
@app.on_event("shutdown")
async def save_registry():
    import pickle
    with open("/var/lib/butterflyfx/registry.pkl", "wb") as f:
        pickle.dump(registry, f)

@app.on_event("startup")
async def load_registry():
    import pickle
    try:
        with open("/var/lib/butterflyfx/registry.pkl", "rb") as f:
            global registry
            registry = pickle.load(f)
    except FileNotFoundError:
        pass
```

---

## Scaling Beyond 15GB

When you need more capacity:

### 1. Redis Backend

```bash
# Install Redis
sudo apt install redis-server -y

# Update server/registry.py to use Redis
```

### 2. Load Balancer

```nginx
upstream butterflyfx_cluster {
    server 10.0.0.1:8000;
    server 10.0.0.2:8000;
    server 10.0.0.3:8000;
}
```

---

## Troubleshooting

**Server won't start:**
```bash
# Check logs
sudo journalctl -u butterflyfx -n 50

# Check port
sudo netstat -tulpn | grep 8000
```

**High memory usage:**
```bash
# Check process
ps aux | grep uvicorn

# Monitor memory
watch -n 1 'free -h'
```

**Slow responses:**
```bash
# Check worker count
# Increase workers if CPU usage is low
```

---

**Ready to deploy!** 🚀

