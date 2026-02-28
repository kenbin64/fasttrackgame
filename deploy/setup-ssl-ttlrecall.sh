#!/bin/bash
#
# SSL Certificate Setup for ttlrecall.com
# 
# Copyright (c) 2024-2026 Kenneth Bingham
# Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
#
# This script sets up free SSL certificates using Let's Encrypt
# for ttlrecall.com and all alternative domains.
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PRIMARY_DOMAIN="ttlrecall.com"
ALT_DOMAINS="www.ttlrecall.com theconduit.me www.theconduit.me valuesai.online www.valuesai.online"
EMAIL="support@ttlrecall.com"
VPS_IP="172.81.62.217"

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  SSL Certificate Setup for ttlrecall.com                    ║${NC}"
echo -e "${GREEN}║  ButterflyFX AI - Secure Deployment                         ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Please run as root (sudo)${NC}"
    exit 1
fi

# Step 1: Install Certbot
echo -e "${YELLOW}[1/6] Installing Certbot...${NC}"
apt update
apt install -y certbot python3-certbot-nginx

# Step 2: Verify DNS configuration
echo -e "${YELLOW}[2/6] Verifying DNS configuration...${NC}"
echo "Checking if domains point to VPS IP: $VPS_IP"

for domain in $PRIMARY_DOMAIN $ALT_DOMAINS; do
    echo -n "  Checking $domain... "
    RESOLVED_IP=$(dig +short $domain | tail -n1)
    
    if [ "$RESOLVED_IP" == "$VPS_IP" ]; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗ (points to $RESOLVED_IP instead of $VPS_IP)${NC}"
        echo -e "${YELLOW}Warning: $domain DNS not configured correctly${NC}"
        echo "Please update DNS A record to point to $VPS_IP"
    fi
done

# Step 3: Configure Nginx for HTTP (pre-SSL)
echo -e "${YELLOW}[3/6] Configuring Nginx for HTTP...${NC}"

cat > /etc/nginx/sites-available/ttlrecall.com << 'EOF'
# HTTP server (for Let's Encrypt verification)
server {
    listen 80;
    listen [::]:80;
    server_name ttlrecall.com www.ttlrecall.com;
    
    # Let's Encrypt verification
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect to HTTPS (will be enabled after SSL setup)
    # location / {
    #     return 301 https://$server_name$request_uri;
    # }
    
    # Temporary: serve static files
    location / {
        root /var/www/ttlrecall/web/ttlrecall;
        try_files $uri $uri/ /index.html;
    }
}
EOF

# Create certbot directory
mkdir -p /var/www/certbot

# Enable site
ln -sf /etc/nginx/sites-available/ttlrecall.com /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# Step 4: Obtain SSL certificates
echo -e "${YELLOW}[4/6] Obtaining SSL certificates from Let's Encrypt...${NC}"

# Build domain list
DOMAIN_ARGS="-d $PRIMARY_DOMAIN"
for domain in $ALT_DOMAINS; do
    DOMAIN_ARGS="$DOMAIN_ARGS -d $domain"
done

# Request certificate
certbot certonly \
    --nginx \
    $DOMAIN_ARGS \
    --email $EMAIL \
    --agree-tos \
    --non-interactive \
    --expand

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ SSL certificates obtained successfully${NC}"
else
    echo -e "${RED}✗ Failed to obtain SSL certificates${NC}"
    echo "Please check:"
    echo "  1. DNS records point to $VPS_IP"
    echo "  2. Port 80 is open in firewall"
    echo "  3. Nginx is running"
    exit 1
fi

# Step 5: Configure Nginx with SSL
echo -e "${YELLOW}[5/6] Configuring Nginx with SSL...${NC}"

cat > /etc/nginx/sites-available/ttlrecall.com << 'EOF'
# HTTP -> HTTPS redirect
server {
    listen 80;
    listen [::]:80;
    server_name ttlrecall.com www.ttlrecall.com theconduit.me www.theconduit.me valuesai.online www.valuesai.online;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS server - ttlrecall.com (primary)
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name ttlrecall.com www.ttlrecall.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/ttlrecall.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ttlrecall.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_timeout 10m;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Content Security Policy
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' wss: ws:;" always;
    
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

# Alternative domains - redirect to primary
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name theconduit.me www.theconduit.me valuesai.online www.valuesai.online;
    
    ssl_certificate /etc/letsencrypt/live/ttlrecall.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ttlrecall.com/privkey.pem;
    
    return 301 https://ttlrecall.com$request_uri;
}
EOF

# Test and reload Nginx
nginx -t && systemctl reload nginx

# Step 6: Setup auto-renewal
echo -e "${YELLOW}[6/6] Setting up automatic renewal...${NC}"

# Test renewal
certbot renew --dry-run

# Add cron job for auto-renewal
CRON_CMD="0 3 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'"
(crontab -l 2>/dev/null | grep -v "certbot renew"; echo "$CRON_CMD") | crontab -

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  SSL Setup Complete!                                        ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓ SSL certificates installed${NC}"
echo -e "${GREEN}✓ HTTPS enabled for all domains${NC}"
echo -e "${GREEN}✓ Auto-renewal configured${NC}"
echo ""
echo "Your sites are now accessible at:"
echo "  • https://ttlrecall.com"
echo "  • https://www.ttlrecall.com"
echo "  • https://theconduit.me (redirects to ttlrecall.com)"
echo "  • https://valuesai.online (redirects to ttlrecall.com)"
echo ""
echo "Certificate details:"
certbot certificates
echo ""
echo "Next renewal: $(date -d '+90 days' '+%Y-%m-%d')"
echo ""
echo -e "${YELLOW}Note: Certificates will auto-renew every 90 days${NC}"
