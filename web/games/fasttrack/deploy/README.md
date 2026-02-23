# Fast Track Deployment Guide

## kensgames.com Production Setup

**VPS:** 172.81.62.217  
**Domain:** kensgames.com  
**SSL:** Let's Encrypt (auto-renewing)

---

## Quick Start

### 1. DNS Setup (at your registrar)

Add these records:
```
A    @       172.81.62.217
A    www     172.81.62.217
```

### 2. SSH to VPS

```bash
ssh root@172.81.62.217
```

### 3. Clone Repository

```bash
cd /opt
git clone https://github.com/kenbin64/fasttrackgame.git butterflyfx/dimensionsos
cd butterflyfx/dimensionsos/web/games/fasttrack
```

### 4. Run Deployment Script

```bash
sudo bash deploy/deploy_kensgames.sh
```

This will:
- Install nginx, certbot, Python dependencies
- Obtain SSL certificate from Let's Encrypt
- Configure nginx with WSS proxy
- Create systemd services for lobby server
- Configure UFW firewall
- Set up auto-renewal for SSL

---

## Manual Steps (if script fails)

### Install Dependencies

```bash
apt-get update
apt-get install -y nginx certbot python3-certbot-nginx python3 python3-pip python3-venv git
```

### SSL Certificate

```bash
certbot --nginx -d kensgames.com -d www.kensgames.com
```

### Install Nginx Config

```bash
cp deploy/nginx.conf /etc/nginx/sites-available/kensgames.com
ln -sf /etc/nginx/sites-available/kensgames.com /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
```

### Start Lobby Server

```bash
cd /opt/butterflyfx/dimensionsos/web/games/fasttrack
python3 -m venv venv
source venv/bin/activate
pip install websockets aiohttp
python3 server/lobby_server.py --host 127.0.0.1 --port 8765
```

---

## URLs

| Purpose | URL |
|---------|-----|
| 🎮 Game | https://kensgames.com/fasttrack |
| 📱 Mobile | https://kensgames.com/mobile |
| 🔌 WebSocket | wss://kensgames.com/ws |
| 📊 Manifold | wss://kensgames.com/manifold |

---

## Service Management

```bash
# Start/stop lobby server
systemctl start fasttrack-lobby
systemctl stop fasttrack-lobby
systemctl restart fasttrack-lobby

# View logs
journalctl -u fasttrack-lobby -f

# Check status
systemctl status fasttrack-lobby
```

---

## SSL Certificate Renewal

Certificates auto-renew via cron. To test:

```bash
certbot renew --dry-run
```

---

## PWA Installation

Users can install Fast Track as an app:

| Platform | How to Install |
|----------|----------------|
| **Android** | Banner appears, or Menu → "Add to Home Screen" |
| **iOS** | Safari → Share ⬆️ → "Add to Home Screen" |
| **Windows/Mac** | Chrome/Edge address bar → Install icon |

---

## Architecture

```
┌───────────────────────────────────────────────────────┐
│                    INTERNET                           │
└─────────────────────────┬─────────────────────────────┘
                          │ HTTPS (443)
┌─────────────────────────▼─────────────────────────────┐
│                      NGINX                            │
│  • SSL termination (Let's Encrypt)                    │
│  • Static file serving                                │
│  • WebSocket proxy to localhost:8765                  │
│  • Rate limiting (30 req/s)                           │
└─────────────────────────┬─────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────────┐
│  Static      │ │   Lobby      │ │   Manifold       │
│  Files       │ │   Server     │ │   Server         │
│  /fasttrack  │ │   :8765      │ │   :8766          │
│              │ │  (WebSocket) │ │  (Future)        │
└──────────────┘ └──────────────┘ └──────────────────┘
```

---

## Firewall Rules (UFW)

```bash
sudo ufw allow 'Nginx Full'  # 80, 443
sudo ufw allow ssh           # 22
sudo ufw enable
```

---

## Troubleshooting

### WebSocket not connecting

1. Check nginx config: `nginx -t`
2. Check lobby server: `systemctl status fasttrack-lobby`
3. Check logs: `journalctl -u fasttrack-lobby -f`

### SSL issues

1. Check cert dates: `certbot certificates`
2. Force renewal: `certbot renew --force-renewal`
3. Check DNS propagation: `dig kensgames.com`

### 502 Bad Gateway

1. Lobby server not running: `systemctl start fasttrack-lobby`
2. Wrong port: check nginx upstream config

---

## Updates

```bash
cd /opt/butterflyfx/dimensionsos
git pull origin main
systemctl restart fasttrack-lobby
```

---

## Contact

- **Domain:** kensgames.com
- **Repository:** https://github.com/kenbin64/fasttrackgame
