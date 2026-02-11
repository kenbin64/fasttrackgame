# 🚀 ButterflyFx Platform - Complete VPS Deployment Guide

Complete guide to deploy the ButterflyFx multi-product platform to production VPS with 11 domains, SSL certificates, and public landing pages.

---

## 📋 Server Information

- **VPS IP**: 172.81.62.217
- **OS**: Ubuntu 22.04 LTS
- **Domains**: 11 domains (all pointing to VPS)
- **Platform**: Multi-product with unified authentication

---

## 🌐 Domain Mapping Strategy

### **Primary Platform Domains**

1. **butterflyfx.us** → Main Platform Website
   - Landing page (public)
   - Login/Register
   - Dashboard (authenticated)
   - Product routing

2. **dimensionos.net** → DimensionOS Branding
   - Alternative domain for platform
   - Same content as butterflyfx.us

### **Product Domains**

3. **butterflyfxhd.com** → Universal Hard Drive Product
   - Public landing page
   - Product demo/screenshots
   - Pricing
   - Login → Hard Drive app

4. **theconduit.me** → Universal Connector Product
   - Public landing page
   - Connector showcase
   - Integration examples
   - Login → Connector app

5. **gnopping.com** → Python API Product
   - Public landing page
   - API documentation
   - Code examples
   - Login → API dashboard

6. **tetracubedb.com** → Database/Storage Product
   - Public landing page
   - Database features
   - Performance metrics
   - Login → Database app

### **Future/Special Purpose Domains**

7. **keneticarts.com** → Creative/Art Applications
   - Future: Image/Video substrate apps
   - Pattern generation tools

8. **valuesai.online** → AI Integration
   - Future: AI-powered substrate analysis
   - Machine learning features

9. **ttlrecall.com** → Memory/Recall Features
   - Future: Expanding memory system
   - Knowledge graph visualization

10. **unwalledgarden.us** → Open Platform/Community
    - Future: Community features
    - Open source components (non-secret sauce)

11. **principiapizzeria.xyz** → Fun/Demo Domain
    - Interactive demos
    - Tutorials
    - Playground

---

## 🔧 Server Requirements

**Minimum:**
- Ubuntu 22.04 LTS
- 8 GB RAM
- 4 CPU cores
- Python 3.11+
- 50 GB SSD

**Recommended:**
- Ubuntu 22.04 LTS
- 16 GB RAM
- 8 CPU cores
- Python 3.11+
- 100 GB SSD

## 🛠️ Step 1: Initial Server Setup

### 1.1 SSH into VPS

```bash
# SSH into VPS
ssh root@172.81.62.217
```

### 1.2 Update System

```bash
# Update system packages
apt update && apt upgrade -y

# Install required packages
apt install -y \
    python3.11 \
    python3-pip \
    python3-venv \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    ufw \
    htop
```

### 1.3 Create Deployment User

```bash
# Create butterflyfx user
adduser butterflyfx

# Add to sudo group
usermod -aG sudo butterflyfx

# Switch to butterflyfx user
su - butterflyfx
```

---

## 📦 Step 2: Clone Repository

### 2.1 Clone from GitHub

```bash
# Create app directory
mkdir -p /home/butterflyfx/apps
cd /home/butterflyfx/apps

# Clone repository
git clone https://github.com/kenbin64/butterflyfxpython.git
cd butterflyfxpython
```

### 2.2 Create Virtual Environment

```bash
# Create virtual environment
python3.11 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 2.3 Install Dependencies

```bash
# Create requirements.txt if not exists
cat > requirements.txt << EOF
Flask==3.0.0
gunicorn==21.2.0
python-dotenv==1.0.0
cryptography==41.0.7
Pillow==10.1.0
numpy==1.26.2
requests==2.31.0
EOF

# Install dependencies
pip install -r requirements.txt
```

---

## 🔐 Step 3: Environment Configuration

### 3.1 Create Environment File

```bash
# Create .env file
cat > .env << EOF
FLASK_ENV=production
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
DATABASE_PATH=/home/butterflyfx/data/butterflyfx.db
MASTER_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
ALLOWED_HOSTS=butterflyfx.us,dimensionos.net,butterflyfxhd.com,theconduit.me,gnopping.com,tetracubedb.com,keneticarts.com,valuesai.online,ttlrecall.com,unwalledgarden.us,principiapizzeria.xyz
EOF

# Secure the .env file
chmod 600 .env
```

### 3.2 Create Data Directory

```bash
# Create data directory
mkdir -p /home/butterflyfx/data

# Secure data directory
chmod 700 /home/butterflyfx/data
```

---

## 🔒 Step 4: Closed Source Protection

### 4.1 Create .gitignore

```bash
# Create .gitignore for secret sauce
cat > .gitignore << EOF
# Secret sauce - DO NOT COMMIT TO PUBLIC REPO
kernel/position_substrate.py
kernel/dimensional_relationships.py
kernel/universal_harddrive.py
kernel/substrate_table.py
kernel/knowledge_seeding.py

# Environment
.env
*.pyc
__pycache__/
.venv/
venv/

# Data
*.db
*.sqlite
*.sqlite3
data/

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

### 4.2 Deployment Strategy

**For closed source deployment:**
1. Keep full code on VPS only
2. Push only non-secret files to GitHub
3. Use private repository until patent is obtained
4. Deploy directly to VPS (not through GitHub)

```bash
# Initialize git (if not already done)
git init

# Add .gitignore
git add .gitignore
git commit -m "Add gitignore for secret sauce"
```

---

## 🚀 Step 5: Systemd Service Setup

### 5.1 Create Log Directory

```bash
# Create log directory
sudo mkdir -p /var/log/butterflyfx

# Set ownership
sudo chown butterflyfx:butterflyfx /var/log/butterflyfx
```

### 5.2 Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/butterflyfx.service
```

**Service Configuration:**

```ini
[Unit]
Description=ButterflyFx Platform
After=network.target

[Service]
Type=notify
User=butterflyfx
Group=butterflyfx
WorkingDirectory=/home/butterflyfx/apps/butterflyfxpython
Environment="PATH=/home/butterflyfx/apps/butterflyfxpython/.venv/bin"
ExecStart=/home/butterflyfx/apps/butterflyfxpython/.venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/home/butterflyfx/butterflyfx.sock \
    --timeout 120 \
    --access-logfile /var/log/butterflyfx/access.log \
    --error-logfile /var/log/butterflyfx/error.log \
    platform.web.app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 5.3 Enable and Start Service

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

## 🌐 Step 6: Nginx Configuration for All Domains

### 6.1 Remove Default Site

```bash
# Remove default nginx site
sudo rm /etc/nginx/sites-enabled/default
```

### 6.2 Main Platform Configuration (butterflyfx.us + dimensionos.net)

```bash
# Create main platform config
sudo nano /etc/nginx/sites-available/butterflyfx-main
```

**Configuration:**

```nginx
server {
    listen 80;
    server_name butterflyfx.us www.butterflyfx.us dimensionos.net www.dimensionos.net;

    client_max_body_size 100M;

    location / {
        proxy_pass http://unix:/home/butterflyfx/butterflyfx.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /static {
        alias /home/butterflyfx/apps/butterflyfxpython/platform/web/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 6.3 Universal Hard Drive Configuration (butterflyfxhd.com)

```bash
# Create hard drive config
sudo nano /etc/nginx/sites-available/butterflyfx-harddrive
```

**Configuration:**

```nginx
server {
    listen 80;
    server_name butterflyfxhd.com www.butterflyfxhd.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://unix:/home/butterflyfx/butterflyfx.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Product harddrive;
    }

    location /static {
        alias /home/butterflyfx/apps/butterflyfxpython/platform/web/static;
        expires 30d;
    }
}
```

### 6.4 Universal Connector Configuration (theconduit.me)

```bash
# Create connector config
sudo nano /etc/nginx/sites-available/butterflyfx-connector
```

**Configuration:**

```nginx
server {
    listen 80;
    server_name theconduit.me www.theconduit.me;

    client_max_body_size 100M;

    location / {
        proxy_pass http://unix:/home/butterflyfx/butterflyfx.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Product connector;
    }

    location /static {
        alias /home/butterflyfx/apps/butterflyfxpython/platform/web/static;
        expires 30d;
    }
}
```

### 6.5 Python API Configuration (gnopping.com)

```bash
# Create Python API config
sudo nano /etc/nginx/sites-available/butterflyfx-pythonapi
```

**Configuration:**

```nginx
server {
    listen 80;
    server_name gnopping.com www.gnopping.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://unix:/home/butterflyfx/butterflyfx.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Product pythonapi;
    }

    location /static {
        alias /home/butterflyfx/apps/butterflyfxpython/platform/web/static;
        expires 30d;
    }
}
```

### 6.6 Database Configuration (tetracubedb.com)

```bash
# Create database config
sudo nano /etc/nginx/sites-available/butterflyfx-database
```

**Configuration:**

```nginx
server {
    listen 80;
    server_name tetracubedb.com www.tetracubedb.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://unix:/home/butterflyfx/butterflyfx.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Product database;
    }

    location /static {
        alias /home/butterflyfx/apps/butterflyfxpython/platform/web/static;
        expires 30d;
    }
}
```

### 6.7 Future Domains Configuration

```bash
# Create future domains config
sudo nano /etc/nginx/sites-available/butterflyfx-future
```

**Configuration:**

```nginx
# Kenetic Arts
server {
    listen 80;
    server_name keneticarts.com www.keneticarts.com;
    return 301 https://butterflyfx.us$request_uri;
}

# Values AI
server {
    listen 80;
    server_name valuesai.online www.valuesai.online;
    return 301 https://butterflyfx.us$request_uri;
}

# TTL Recall
server {
    listen 80;
    server_name ttlrecall.com www.ttlrecall.com;
    return 301 https://butterflyfx.us$request_uri;
}

# Unwalled Garden
server {
    listen 80;
    server_name unwalledgarden.us www.unwalledgarden.us;
    return 301 https://butterflyfx.us$request_uri;
}

# Principia Pizzeria
server {
    listen 80;
    server_name principiapizzeria.xyz www.principiapizzeria.xyz;
    return 301 https://butterflyfx.us$request_uri;
}
```

### 6.8 Enable All Sites

```bash
# Enable all sites
sudo ln -s /etc/nginx/sites-available/butterflyfx-main /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/butterflyfx-harddrive /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/butterflyfx-connector /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/butterflyfx-pythonapi /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/butterflyfx-database /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/butterflyfx-future /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx
```

---

## 🔒 Step 7: SSL Certificates (Let's Encrypt)

### 7.1 Install Certbot (Already Done in Step 1)

Certbot was installed in Step 1.2. If not installed:

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### 7.2 Obtain SSL Certificates for All Domains

**Main Platform Domains:**

```bash
# butterflyfx.us + dimensionos.net
sudo certbot --nginx \
    -d butterflyfx.us \
    -d www.butterflyfx.us \
    -d dimensionos.net \
    -d www.dimensionos.net
```

**Product Domains:**

```bash
# Universal Hard Drive
sudo certbot --nginx \
    -d butterflyfxhd.com \
    -d www.butterflyfxhd.com

# Universal Connector
sudo certbot --nginx \
    -d theconduit.me \
    -d www.theconduit.me

# Python API
sudo certbot --nginx \
    -d gnopping.com \
    -d www.gnopping.com

# Database
sudo certbot --nginx \
    -d tetracubedb.com \
    -d www.tetracubedb.com
```

**Future Domains:**

```bash
# Kenetic Arts
sudo certbot --nginx \
    -d keneticarts.com \
    -d www.keneticarts.com

# Values AI
sudo certbot --nginx \
    -d valuesai.online \
    -d www.valuesai.online

# TTL Recall
sudo certbot --nginx \
    -d ttlrecall.com \
    -d www.ttlrecall.com

# Unwalled Garden
sudo certbot --nginx \
    -d unwalledgarden.us \
    -d www.unwalledgarden.us

# Principia Pizzeria
sudo certbot --nginx \
    -d principiapizzeria.xyz \
    -d www.principiapizzeria.xyz
```

### 7.3 Test Auto-Renewal

```bash
# Test certificate renewal
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

### 7.4 Verify SSL Installation

```bash
# Test each domain
curl -I https://butterflyfx.us
curl -I https://butterflyfxhd.com
curl -I https://theconduit.me
curl -I https://gnopping.com
curl -I https://tetracubedb.com
```

---

## 🔥 Step 8: Firewall Configuration

### 8.1 Configure UFW

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (IMPORTANT!)
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS
sudo ufw allow 443/tcp

# Check status
sudo ufw status verbose
```

---

## 📄 Step 9: Public Landing Pages

Each product domain needs a public landing page (no login required) for marketing and introduction.

### 9.1 Landing Page Requirements

Each landing page should include:
- Product introduction
- Key features showcase
- Screenshots/demos
- Pricing information
- Login/Register buttons
- Documentation links
- Call-to-action

### 9.2 Landing Page Locations

Landing pages will be created in:
- `platform/web/templates/landing/butterflyfx.html` (main platform)
- `platform/web/templates/landing/harddrive.html` (Universal Hard Drive)
- `platform/web/templates/landing/connector.html` (Universal Connector)
- `platform/web/templates/landing/pythonapi.html` (Python API)
- `platform/web/templates/landing/database.html` (Database)

**Note:** Landing pages will be created in a separate step after deployment.

---

## 🧪 Step 10: Testing Deployment

### 10.1 Test Platform Service

```bash
# Check service status
sudo systemctl status butterflyfx

# Check if socket is created
ls -la /home/butterflyfx/butterflyfx.sock

# Test local connection
curl http://localhost/
```

### 10.2 Test All Domains

```bash
# Test main platform
curl -I https://butterflyfx.us
curl -I https://dimensionos.net

# Test products
curl -I https://butterflyfxhd.com
curl -I https://theconduit.me
curl -I https://gnopping.com
curl -I https://tetracubedb.com

# Test future domains (should redirect)
curl -I https://keneticarts.com
curl -I https://valuesai.online
```

### 10.3 Test Authentication

```bash
# Test login endpoint
curl -X POST https://butterflyfx.us/login \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=demo_free&password=demo123"
```

---

## 📊 Step 11: Monitoring

### 11.1 System Resources

```bash
# Monitor in real-time
htop

# Check disk usage
df -h

# Check memory usage
free -h
```

### 11.2 Application Logs

```bash
# Follow application logs
sudo journalctl -u butterflyfx -f

# Last 100 lines
sudo journalctl -u butterflyfx -n 100

# Check error log
sudo tail -f /var/log/butterflyfx/error.log

# Check access log
sudo tail -f /var/log/butterflyfx/access.log
```

### 11.3 Nginx Logs

```bash
# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Check nginx access log
sudo tail -f /var/log/nginx/access.log
```

---

## ⚡ Step 12: Performance Tuning

### 12.1 Increase File Descriptors

```bash
# Edit limits
sudo nano /etc/security/limits.conf

# Add these lines:
* soft nofile 65536
* hard nofile 65536
```

### 12.2 Optimize Kernel

```bash
# Edit sysctl
sudo nano /etc/sysctl.conf

# Add these lines:
net.core.somaxconn = 65536
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_tw_reuse = 1
```

**Apply changes:**

```bash
sudo sysctl -p
```

### 12.3 Optimize Gunicorn Workers

```bash
# Calculate optimal workers: (2 x CPU cores) + 1
# For 8 cores: (2 x 8) + 1 = 17 workers

# Edit systemd service
sudo nano /etc/systemd/system/butterflyfx.service

# Change --workers 4 to --workers 17
# Then reload:
sudo systemctl daemon-reload
sudo systemctl restart butterflyfx
```

---

## 💾 Step 13: Backup Strategy

### 13.1 Create Backup Script

```bash
# Create backup directory
sudo mkdir -p /home/butterflyfx/backups

# Create backup script
cat > /home/butterflyfx/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/butterflyfx/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="butterflyfx_backup_${DATE}.tar.gz"

# Backup data directory
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    /home/butterflyfx/data \
    /home/butterflyfx/apps/butterflyfxpython/.env

# Keep only last 7 backups
cd "${BACKUP_DIR}"
ls -t | tail -n +8 | xargs -r rm

echo "Backup completed: ${BACKUP_FILE}"
EOF

# Make executable
chmod +x /home/butterflyfx/backup.sh
```

### 13.2 Schedule Daily Backups

```bash
# Add to crontab
crontab -e

# Add this line (backup at 2 AM daily):
0 2 * * * /home/butterflyfx/backup.sh >> /var/log/butterflyfx/backup.log 2>&1
```

---

## 🔄 Step 14: Update and Maintenance

### 14.1 Update Application

```bash
# SSH into VPS
ssh butterflyfx@172.81.62.217

# Navigate to app directory
cd /home/butterflyfx/apps/butterflyfxpython

# Pull latest changes (if using git)
git pull origin main

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart butterflyfx

# Check status
sudo systemctl status butterflyfx
```

### 14.2 Update System Packages

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Reboot if kernel updated
sudo reboot
```

---

## 🐛 Step 15: Troubleshooting

### 15.1 Service Won't Start

```bash
# Check service status
sudo systemctl status butterflyfx

# Check logs
sudo journalctl -u butterflyfx -n 50

# Check if socket exists
ls -la /home/butterflyfx/butterflyfx.sock

# Check permissions
sudo chown butterflyfx:butterflyfx /home/butterflyfx/butterflyfx.sock
```

### 15.2 Nginx Errors

```bash
# Test nginx configuration
sudo nginx -t

# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

### 15.3 SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Renew certificates manually
sudo certbot renew

# Force renewal
sudo certbot renew --force-renewal
```

### 15.4 High Memory Usage

```bash
# Check memory usage
free -h

# Check process memory
ps aux --sort=-%mem | head -10

# Restart service to clear memory
sudo systemctl restart butterflyfx
```

### 15.5 Slow Response Times

```bash
# Check worker count
ps aux | grep gunicorn

# Increase workers in systemd service
sudo nano /etc/systemd/system/butterflyfx.service

# Check nginx access log for slow requests
sudo tail -f /var/log/nginx/access.log
```

---

## 📋 Step 16: Deployment Checklist

### Pre-Deployment

- [ ] VPS accessible via SSH (172.81.62.217)
- [ ] All 11 domains pointing to VPS IP
- [ ] GitHub repository ready
- [ ] Secret sauce files identified

### Deployment

- [ ] System updated and packages installed
- [ ] Deployment user created (butterflyfx)
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Environment file configured (.env)
- [ ] Data directory created
- [ ] .gitignore configured for secret sauce
- [ ] Systemd service created and enabled
- [ ] Nginx configurations created for all domains
- [ ] All nginx sites enabled
- [ ] SSL certificates installed for all domains
- [ ] Firewall configured (UFW)

### Post-Deployment

- [ ] Service running successfully
- [ ] All domains accessible via HTTPS
- [ ] Authentication working
- [ ] Logs being written correctly
- [ ] Backup script configured
- [ ] Monitoring set up

### Future Tasks

- [ ] Create public landing pages
- [ ] Implement payment integration
- [ ] Create Python package (pip)
- [ ] Deploy to PyPI
- [ ] Create Node.js bindings
- [ ] Obtain patent for secret sauce
- [ ] Open source non-secret components

---

## 🎯 Quick Reference

### Service Management

```bash
# Start service
sudo systemctl start butterflyfx

# Stop service
sudo systemctl stop butterflyfx

# Restart service
sudo systemctl restart butterflyfx

# Check status
sudo systemctl status butterflyfx

# View logs
sudo journalctl -u butterflyfx -f
```

### Nginx Management

```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

### SSL Management

```bash
# List certificates
sudo certbot certificates

# Renew all certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

---

## 🌐 Domain Summary

| Domain | Purpose | Status |
|--------|---------|--------|
| butterflyfx.us | Main Platform | Active |
| dimensionos.net | Platform (Alt) | Active |
| butterflyfxhd.com | Universal Hard Drive | Active |
| theconduit.me | Universal Connector | Active |
| gnopping.com | Python API | Active |
| tetracubedb.com | Database/Storage | Active |
| keneticarts.com | Creative Apps | Redirect to main |
| valuesai.online | AI Features | Redirect to main |
| ttlrecall.com | Memory/Recall | Redirect to main |
| unwalledgarden.us | Community | Redirect to main |
| principiapizzeria.xyz | Demos/Playground | Redirect to main |

---

## 🚀 **Deployment Complete!**

Your ButterflyFx platform is now deployed with:
- ✅ 11 domains configured
- ✅ SSL certificates installed
- ✅ Unified authentication system
- ✅ Multi-product architecture
- ✅ Closed source protection
- ✅ Monitoring and logging
- ✅ Backup strategy

**Next Steps:**
1. Create public landing pages for each product
2. Test all authentication flows
3. Implement payment integration
4. Create Python package for PyPI

**Platform URLs:**
- Main: https://butterflyfx.us
- Hard Drive: https://butterflyfxhd.com
- Connector: https://theconduit.me
- Python API: https://gnopping.com
- Database: https://tetracubedb.com

🦋 **ButterflyFx Platform is live!** ✨

