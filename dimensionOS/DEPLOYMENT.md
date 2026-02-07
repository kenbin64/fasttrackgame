# DimensionOS Deployment Guide

This guide covers deploying DimensionOS to production at https://dimensionos.net

## Prerequisites

- Ubuntu 20.04+ or similar Linux server
- Domain name (dimensionos.net) pointing to your server
- Root or sudo access
- Python 3.10+

## Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv nginx certbot python3-certbot-nginx git

# Create application user (optional, for security)
sudo useradd -m -s /bin/bash dimensionos
```

## Step 2: Clone and Setup Application

```bash
# Clone repository (or upload files)
cd /var/www
sudo git clone <your-repo> butterflyfx
cd butterflyfx/dimensionOS

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Set the following in `.env`:
- `SECRET_KEY`: Generate with `python -c "import os; print(os.urandom(24).hex())"`
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: From Google Cloud Console
- `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`: From GitHub Developer Settings
- `FLASK_ENV=production`
- `SERVER_NAME=dimensionos.net`

## Step 4: Setup OAuth Applications

### Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "DimensionOS"
3. Enable "Google+ API"
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized redirect URIs:
   - `https://dimensionos.net/authorize/google`
   - `https://www.dimensionos.net/authorize/google`
7. Copy Client ID and Client Secret to `.env`

### GitHub OAuth

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Application name: "DimensionOS"
4. Homepage URL: `https://dimensionos.net`
5. Authorization callback URL: `https://dimensionos.net/authorize/github`
6. Copy Client ID and Client Secret to `.env`

## Step 5: SSL Certificate with Let's Encrypt

```bash
# Stop nginx if running
sudo systemctl stop nginx

# Get SSL certificate
sudo certbot certonly --standalone -d dimensionos.net -d www.dimensionos.net

# Certificates will be at:
# /etc/letsencrypt/live/dimensionos.net/fullchain.pem
# /etc/letsencrypt/live/dimensionos.net/privkey.pem
```

## Step 6: Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/dimensionos.net

# Edit paths in the config
sudo nano /etc/nginx/sites-available/dimensionos.net
# Update: /path/to/butterflyfx/dimensionOS/static

# Enable site
sudo ln -s /etc/nginx/sites-available/dimensionos.net /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

## Step 7: Setup Gunicorn Service

```bash
# Create log directory
sudo mkdir -p /var/log/dimensionos
sudo chown www-data:www-data /var/log/dimensionos

# Edit gunicorn config paths
nano gunicorn_config.py
# Update log paths if needed

# Copy systemd service file
sudo cp dimensionos.service /etc/systemd/system/

# Edit service file
sudo nano /etc/systemd/system/dimensionos.service
# Update paths:
#   WorkingDirectory=/var/www/butterflyfx/dimensionOS
#   Environment="PATH=/var/www/butterflyfx/.venv/bin"
#   ExecStart=/var/www/butterflyfx/.venv/bin/gunicorn -c gunicorn_config.py app:app

# Reload systemd
sudo systemctl daemon-reload

# Start DimensionOS
sudo systemctl start dimensionos
sudo systemctl enable dimensionos

# Check status
sudo systemctl status dimensionos
```

## Step 8: Verify Deployment

```bash
# Check if gunicorn is running
sudo systemctl status dimensionos

# Check nginx
sudo systemctl status nginx

# View logs
sudo journalctl -u dimensionos -f
sudo tail -f /var/log/nginx/dimensionos_error.log
```

Visit https://dimensionos.net - you should see the landing page!

## Step 9: SSL Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up a cron job for renewal
# Verify it exists:
sudo systemctl list-timers | grep certbot
```

## Maintenance Commands

```bash
# Restart DimensionOS
sudo systemctl restart dimensionos

# View logs
sudo journalctl -u dimensionos -n 100
sudo tail -f /var/log/dimensionos/error.log

# Reload nginx (after config changes)
sudo nginx -t && sudo systemctl reload nginx

# Update application
cd /var/www/butterflyfx
git pull
cd dimensionOS
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart dimensionos
```

## Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp  # SSH
sudo ufw enable
```

## Troubleshooting

### Application won't start

```bash
# Check logs
sudo journalctl -u dimensionos -n 50

# Test manually
cd /var/www/butterflyfx/dimensionOS
source .venv/bin/activate
gunicorn -c gunicorn_config.py app:app
```

### SSL issues

```bash
# Verify certificates
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal
sudo systemctl reload nginx
```

### OAuth not working

- Verify redirect URIs in Google/GitHub match exactly
- Check `.env` has correct client IDs and secrets
- Ensure `SERVER_NAME` in `.env` matches your domain

## Security Checklist

- [ ] SSL certificate installed and auto-renewal configured
- [ ] Firewall configured (only ports 22, 80, 443 open)
- [ ] Strong `SECRET_KEY` in `.env`
- [ ] `.env` file has restricted permissions (600)
- [ ] Application running as non-root user
- [ ] Regular backups configured
- [ ] Security headers enabled in nginx
- [ ] Keep system and dependencies updated

## Backup

```bash
# Backup .env file
sudo cp /var/www/butterflyfx/dimensionOS/.env ~/dimensionos_env_backup

# Backup user data (if using local storage)
sudo tar -czf ~/dimensionos_data_backup.tar.gz /var/www/butterflyfx/dimensionOS/dimensionos_data
```

