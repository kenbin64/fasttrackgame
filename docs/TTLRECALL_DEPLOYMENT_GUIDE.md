# TTL Recall - Deployment Guide

**Domain:** ttlrecall.com  
**Project:** ButterflyFX AI - AI That Remembers  
**Version:** 1.0.0  
**Date:** 2026-02-26

---

## Quick Start

```bash
# 1. Clone repository
cd /opt/butterflyfx/dimensionsos

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Run server
python server/dimensional_server_optimized.py --port 8080

# 5. Deploy to production
./deploy/deploy-ttlrecall.sh
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  ttlrecall.com (Frontend)                                       │
│  ─────────────────────────────────────────────────────────────  │
│  • React + TypeScript                                           │
│  • Three.js (3D memory visualization)                           │
│  • Tailwind CSS + shadcn/ui                                     │
│  • WebSocket client (real-time chat)                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTPS/WSS
┌─────────────────────────────────────────────────────────────────┐
│  VPS: 172.81.62.217                                             │
│  ─────────────────────────────────────────────────────────────  │
│  • Nginx (reverse proxy, SSL termination)                       │
│  • Dimensional Server (optimized)                               │
│  • WebSocket server (real-time)                                 │
│  • Authentication service                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI Manifold                                                    │
│  ─────────────────────────────────────────────────────────────  │
│  • DimensionalAI (core intelligence)                            │
│  • MemorySubstrate (O(1) recall)                                │
│  • IntentionSubstrate (helpful, friendly)                       │
│  • OpenAI/Anthropic API (LLM backend)                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Storage                                                        │
│  ─────────────────────────────────────────────────────────────  │
│  • SQLite (development)                                         │
│  • PostgreSQL (production)                                      │
│  • Redis (session cache)                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Domain Configuration

### **Primary Domain: ttlrecall.com**

**DNS Records:**
```
Type    Name              Value                TTL
A       @                 172.81.62.217        3600
A       www               172.81.62.217        3600
CNAME   api               ttlrecall.com        3600
CNAME   ws                ttlrecall.com        3600
TXT     @                 "v=spf1 mx ~all"     3600
```

### **Alternative Domains (Redirect to ttlrecall.com)**

**theconduit.me:**
```
A       @                 172.81.62.217        3600
```

**dimensionsos.net:**
```
A       @                 172.81.62.217        3600
```

**valuesai.online:**
```
A       @                 172.81.62.217        3600
```

---

## Server Setup

### **1. Install Dependencies**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install Nginx
sudo apt install nginx -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Redis
sudo apt install redis-server -y

# Install certbot (SSL)
sudo apt install certbot python3-certbot-nginx -y
```

### **2. Create Application User**

```bash
# Create user
sudo useradd -m -s /bin/bash ttlrecall

# Create directories
sudo mkdir -p /var/www/ttlrecall
sudo chown ttlrecall:ttlrecall /var/www/ttlrecall

# Switch to user
sudo su - ttlrecall
```

### **3. Deploy Application**

```bash
# Clone repository
cd /var/www/ttlrecall
git clone https://github.com/yourusername/butterflyfx.git .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install AI dependencies
pip install openai anthropic tiktoken

# Create environment file
cat > .env << EOF
# AI Configuration
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
AI_MODEL=gpt-4

# Database
DATABASE_URL=postgresql://ttlrecall:password@localhost/ttlrecall_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Server
HOST=0.0.0.0
PORT=8080
DEBUG=false

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# CORS
ALLOWED_ORIGINS=https://ttlrecall.com,https://www.ttlrecall.com
EOF

# Set permissions
chmod 600 .env
```

### **4. Configure PostgreSQL**

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE ttlrecall_db;
CREATE USER ttlrecall WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE ttlrecall_db TO ttlrecall;
\q
EOF

# Initialize database
python -c "
from ai.memory_substrate import MemorySubstrate
substrate = MemorySubstrate('postgresql://ttlrecall:password@localhost/ttlrecall_db')
print('Database initialized')
"
```

### **5. Configure Systemd Service**

```bash
# Create service file
sudo cat > /etc/systemd/system/ttlrecall.service << EOF
[Unit]
Description=TTL Recall - ButterflyFX AI
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=ttlrecall
Group=ttlrecall
WorkingDirectory=/var/www/ttlrecall
Environment="PATH=/var/www/ttlrecall/venv/bin"
EnvironmentFile=/var/www/ttlrecall/.env
ExecStart=/var/www/ttlrecall/venv/bin/python server/dimensional_server_optimized.py --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ttlrecall
sudo systemctl start ttlrecall
sudo systemctl status ttlrecall
```

### **6. Configure Nginx**

```bash
# Create Nginx configuration
sudo cat > /etc/nginx/sites-available/ttlrecall.com << 'EOF'
# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name ttlrecall.com www.ttlrecall.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ttlrecall.com www.ttlrecall.com;
    
    # SSL certificates (will be added by certbot)
    ssl_certificate /etc/letsencrypt/live/ttlrecall.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ttlrecall.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Static files
    location / {
        root /var/www/ttlrecall/web/ttlrecall;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://localhost:8080/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket proxy
    location /ws/ {
        proxy_pass http://localhost:8080/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/ttlrecall.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **7. Obtain SSL Certificate**

```bash
# Get certificate
sudo certbot --nginx -d ttlrecall.com -d www.ttlrecall.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Frontend Deployment

### **Build React Application**

```bash
# Navigate to frontend directory
cd /var/www/ttlrecall/web/ttlrecall

# Install dependencies
npm install

# Build for production
npm run build

# Output will be in /var/www/ttlrecall/web/ttlrecall/dist
```

### **Frontend Structure**

```
web/ttlrecall/
├── src/
│   ├── components/
│   │   ├── Chat.tsx              # Main chat interface
│   │   ├── MemoryVisualization.tsx  # 3D memory manifold
│   │   ├── Auth.tsx              # Sign in/up
│   │   └── Dashboard.tsx         # User dashboard
│   ├── lib/
│   │   ├── api.ts                # API client
│   │   ├── websocket.ts          # WebSocket client
│   │   └── dimensional.ts        # Dimensional utilities
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
└── vite.config.ts
```

---

## API Endpoints

### **Authentication**

```
POST   /api/auth/register        - Register new user
POST   /api/auth/login           - Login
POST   /api/auth/logout          - Logout
GET    /api/auth/status          - Check auth status
```

### **AI Chat**

```
POST   /api/chat/message         - Send message to AI
GET    /api/chat/history         - Get conversation history
POST   /api/chat/new             - Start new conversation
```

### **Memory Management**

```
GET    /api/memory/list          - List user memories
GET    /api/memory/:id           - Get specific memory
DELETE /api/memory/:id           - Delete memory
GET    /api/memory/stats         - Get memory statistics
GET    /api/memory/export        - Export all memories (GDPR)
DELETE /api/memory/all           - Delete all memories (GDPR)
```

### **User Management**

```
GET    /api/user/profile         - Get user profile
PUT    /api/user/profile         - Update profile
GET    /api/user/stats           - Get user statistics
DELETE /api/user/account         - Delete account (GDPR)
```

### **WebSocket**

```
WS     /ws/chat                  - Real-time chat
```

---

## Monitoring

### **System Monitoring**

```bash
# Check service status
sudo systemctl status ttlrecall

# View logs
sudo journalctl -u ttlrecall -f

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check resource usage
htop
```

### **Application Monitoring**

```bash
# Get server statistics
curl https://ttlrecall.com/api/stats

# Get memory statistics
curl https://ttlrecall.com/api/memory/stats

# Check health
curl https://ttlrecall.com/api/health
```

---

## Backup Strategy

### **Database Backup**

```bash
# Create backup script
cat > /var/www/ttlrecall/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ttlrecall"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump ttlrecall_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup memories database
cp /var/www/ttlrecall/memories.db $BACKUP_DIR/memories_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.db" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /var/www/ttlrecall/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /var/www/ttlrecall/backup.sh") | crontab -
```

---

## Security Checklist

- ✅ SSL/TLS enabled (HTTPS)
- ✅ Firewall configured (UFW)
- ✅ Database credentials secured
- ✅ API keys in environment variables
- ✅ CORS properly configured
- ✅ Rate limiting enabled
- ✅ SQL injection prevention
- ✅ XSS protection headers
- ✅ CSRF tokens
- ✅ Regular backups
- ✅ Fail2ban for brute force protection

```bash
# Configure firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Performance Optimization

### **Nginx Caching**

```nginx
# Add to nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g inactive=60m;

# In server block
location /api/ {
    proxy_cache api_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
    add_header X-Cache-Status $upstream_cache_status;
    # ... rest of proxy config
}
```

### **Redis Caching**

```python
# In server code
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Cache frequently accessed memories
def get_user_memories_cached(user_id):
    cache_key = f"memories:{user_id}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    memories = memory_substrate.recall(user_id)
    redis_client.setex(cache_key, 300, json.dumps(memories))  # 5 min TTL
    
    return memories
```

---

## Scaling Strategy

### **Vertical Scaling (Current)**
- Upgrade VPS resources
- Optimize database queries
- Enable caching

### **Horizontal Scaling (Future)**
- Load balancer (Nginx)
- Multiple app servers
- PostgreSQL replication
- Redis cluster
- CDN for static assets

---

## Troubleshooting

### **Service Won't Start**

```bash
# Check logs
sudo journalctl -u ttlrecall -n 50

# Check permissions
ls -la /var/www/ttlrecall

# Check environment
sudo -u ttlrecall cat /var/www/ttlrecall/.env
```

### **Database Connection Issues**

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U ttlrecall -d ttlrecall_db -h localhost

# Check credentials in .env
```

### **SSL Certificate Issues**

```bash
# Renew certificate
sudo certbot renew

# Check certificate
sudo certbot certificates
```

---

## Launch Checklist

- [ ] Domain DNS configured
- [ ] SSL certificate obtained
- [ ] Database initialized
- [ ] Environment variables set
- [ ] Service running
- [ ] Nginx configured
- [ ] Firewall enabled
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Frontend deployed
- [ ] API tested
- [ ] WebSocket tested
- [ ] Performance optimized
- [ ] Security hardened
- [ ] Documentation complete

---

## Support

**Documentation:** https://ttlrecall.com/docs  
**API Reference:** https://ttlrecall.com/api/docs  
**GitHub:** https://github.com/yourusername/butterflyfx  
**Email:** support@ttlrecall.com

---

**Version:** 1.0.0  
**Last Updated:** 2026-02-26  
**License:** CC BY 4.0 (Kenneth Bingham)
