# ButterflyFX VPS Deployment Guide

## Quick Start (Ubuntu)

### 1. Upload to VPS

```bash
# From your local machine
scp -r butterflyfx user@your-vps-ip:/home/user/

# Or use git
ssh user@your-vps-ip
git clone https://github.com/kenbin64/butterflyfxpython.git butterflyfx
```

### 2. Run Deployment Script

```bash
cd butterflyfx
sudo bash deploy/deploy.sh
```

This will:
- Install Python 3.11
- Create `/opt/butterflyfx` directory
- Setup systemd service
- Configure firewall
- Start the server

### 3. Access Your Server

```
http://your-vps-ip:8080/
```

---

## Advanced Deployment

### With Domain Name

```bash
sudo bash deploy/deploy.sh --domain yourdomain.com
```

This adds nginx reverse proxy.

### With SSL (HTTPS)

```bash
sudo bash deploy/deploy.sh --domain yourdomain.com --ssl --ssl-email admin@yourdomain.com
```

This adds Let's Encrypt SSL certificate with auto-renewal.

### Custom Port

```bash
sudo bash deploy/deploy.sh --port 3000
```

---

## Manual Deployment

If you prefer manual setup:

### 1. Install Python

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv
```

### 2. Create Directory Structure

```bash
sudo mkdir -p /opt/butterflyfx
sudo cp -r helix server web data /opt/butterflyfx/
cd /opt/butterflyfx
python3.11 -m venv venv
```

### 3. Create Systemd Service

```bash
sudo nano /etc/systemd/system/butterflyfx.service
```

```ini
[Unit]
Description=ButterflyFX Dimensional Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/butterflyfx
ExecStart=/opt/butterflyfx/venv/bin/python server/dimensional_server.py --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable butterflyfx
sudo systemctl start butterflyfx
```

### 5. Open Firewall

```bash
sudo ufw allow 8080/tcp
```

---

## Service Management

```bash
# Check status
sudo systemctl status butterflyfx

# View logs
sudo journalctl -u butterflyfx -f

# Restart
sudo systemctl restart butterflyfx

# Stop
sudo systemctl stop butterflyfx
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Landing page |
| GET | `/api/status` | Server status |
| GET | `/api/demos` | List demos |
| GET | `/api/content` | List content |
| GET | `/api/manifold/evaluate?spiral=0&level=3&position=0` | Evaluate manifold |
| GET | `/manifold/function?type=sin&freq=440` | Get function (binary) |
| POST | `/api/content/register` | Register content |

---

## Demo Pages

- `/graphics3d_demo.html` - Interactive 3D graphics
- `/dimensional_demo.html` - Dimensional presentation navigation
- `/presentation_demo.html` - Timeline presentations

---

## Troubleshooting

### Server won't start

```bash
# Check for port conflicts
sudo lsof -i :8080

# Check logs
sudo journalctl -u butterflyfx --no-pager -n 50
```

### Permission denied

```bash
sudo chown -R www-data:www-data /opt/butterflyfx
```

### Python not found

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11
```

---

## Updating

```bash
cd /opt/butterflyfx
sudo systemctl stop butterflyfx
git pull  # or upload new files
sudo systemctl start butterflyfx
```

---

## Security Recommendations

1. **Use HTTPS**: Always use `--ssl` in production
2. **Firewall**: Only open necessary ports
3. **Updates**: Keep system packages updated
4. **Monitoring**: Check logs regularly
5. **Backups**: Backup `/opt/butterflyfx/data/`
