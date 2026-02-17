#!/bin/bash
#
# ButterflyFX Deployment Script for Ubuntu VPS
#
# Copyright (c) 2024-2026 Kenneth Bingham
# Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
# https://creativecommons.org/licenses/by/4.0/
#
# Part of ButterflyFX Infrastructure - Open source deployment tools.
# Attribution required: Kenneth Bingham - https://butterflyfx.us
#
# ---
# 
# This script sets up a complete ButterflyFX dimensional server on Ubuntu.
# Run with: sudo bash deploy.sh
#
# Requirements:
#   - Ubuntu 20.04+ or Debian 11+
#   - Root or sudo access
#   - At least 1GB RAM, 10GB disk
#

set -e  # Exit on error

# =============================================================================
# CONFIGURATION
# =============================================================================

APP_NAME="butterflyfx"
APP_USER="butterflyfx"
APP_DIR="/opt/butterflyfx"
PYTHON_VERSION="3.11"
PORT=8080
DOMAIN=""  # Set your domain if using nginx
USE_NGINX=false
USE_SSL=false
SSL_EMAIL=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# =============================================================================
# PARSE ARGUMENTS
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --domain)
            DOMAIN="$2"
            USE_NGINX=true
            shift 2
            ;;
        --ssl)
            USE_SSL=true
            shift
            ;;
        --ssl-email)
            SSL_EMAIL="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help)
            echo "ButterflyFX Deployment Script"
            echo ""
            echo "Usage: sudo bash deploy.sh [options]"
            echo ""
            echo "Options:"
            echo "  --domain DOMAIN    Set domain name (enables nginx)"
            echo "  --ssl              Enable SSL with Let's Encrypt"
            echo "  --ssl-email EMAIL  Email for SSL certificate"
            echo "  --port PORT        Server port (default: 8080)"
            echo "  --help             Show this help"
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# =============================================================================
# MAIN DEPLOYMENT
# =============================================================================

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           BUTTERFLYFX DEPLOYMENT SCRIPT                        ║"
    echo "║                                                                 ║"
    echo "║   Setting up dimensional server on Ubuntu VPS                  ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    check_root
    
    log_info "Starting deployment..."
    log_info "  App directory: $APP_DIR"
    log_info "  Port: $PORT"
    log_info "  Domain: ${DOMAIN:-'(none)'}"
    log_info "  SSL: $USE_SSL"
    echo ""
    
    # Step 1: System update
    step_system_update
    
    # Step 2: Install dependencies
    step_install_dependencies
    
    # Step 3: Create user and directories
    step_create_user
    
    # Step 4: Clone/copy application
    step_copy_application
    
    # Step 5: Setup Python environment
    step_setup_python
    
    # Step 6: Setup systemd service
    step_setup_systemd
    
    # Step 7: Setup nginx (optional)
    if [[ "$USE_NGINX" == true ]]; then
        step_setup_nginx
    fi
    
    # Step 8: Setup SSL (optional)
    if [[ "$USE_SSL" == true ]]; then
        step_setup_ssl
    fi
    
    # Step 9: Configure firewall
    step_setup_firewall
    
    # Step 10: Start services
    step_start_services
    
    # Done!
    print_success
}

# =============================================================================
# DEPLOYMENT STEPS
# =============================================================================

step_system_update() {
    log_info "Step 1: Updating system packages..."
    apt-get update -qq
    apt-get upgrade -y -qq
    log_success "System updated"
}

step_install_dependencies() {
    log_info "Step 2: Installing dependencies..."
    
    # Add deadsnakes PPA for Python 3.11+
    apt-get install -y -qq software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || true
    apt-get update -qq
    
    # Install packages
    apt-get install -y -qq \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        python${PYTHON_VERSION}-dev \
        python3-pip \
        git \
        curl \
        wget \
        ufw \
        htop \
        tree
    
    # Install nginx if needed
    if [[ "$USE_NGINX" == true ]]; then
        apt-get install -y -qq nginx
    fi
    
    log_success "Dependencies installed"
}

step_create_user() {
    log_info "Step 3: Creating application user..."
    
    # Create user if not exists
    if ! id "$APP_USER" &>/dev/null; then
        useradd --system --create-home --shell /bin/bash "$APP_USER"
        log_success "User '$APP_USER' created"
    else
        log_warn "User '$APP_USER' already exists"
    fi
    
    # Create directories
    mkdir -p "$APP_DIR"
    mkdir -p "$APP_DIR/logs"
    mkdir -p "$APP_DIR/data"
    mkdir -p "$APP_DIR/web"
    
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    log_success "Directories created"
}

step_copy_application() {
    log_info "Step 4: Copying application files..."
    
    # Get the script's directory (where the repo is)
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    REPO_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Check if we're running from within the repo
    if [[ -d "$REPO_DIR/helix" ]]; then
        log_info "  Copying from local repository..."
        cp -r "$REPO_DIR/helix" "$APP_DIR/"
        cp -r "$REPO_DIR/server" "$APP_DIR/"
        cp -r "$REPO_DIR/web" "$APP_DIR/"
        cp -r "$REPO_DIR/data" "$APP_DIR/" 2>/dev/null || true
        cp -r "$REPO_DIR/apps" "$APP_DIR/" 2>/dev/null || true
        cp "$REPO_DIR/README.md" "$APP_DIR/" 2>/dev/null || true
    else
        log_warn "Repository not found locally, creating minimal structure..."
        
        # Create minimal server file
        cat > "$APP_DIR/server/dimensional_server.py" << 'SERVEREOF'
# Minimal dimensional server - replace with full version from repo
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
os.chdir('/opt/butterflyfx/web')
HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler).serve_forever()
SERVEREOF
    fi
    
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    
    log_success "Application files copied"
}

step_setup_python() {
    log_info "Step 5: Setting up Python virtual environment..."
    
    # Create venv
    sudo -u "$APP_USER" python${PYTHON_VERSION} -m venv "$APP_DIR/venv"
    
    # Upgrade pip
    sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install --upgrade pip wheel
    
    # Install any requirements if they exist
    if [[ -f "$APP_DIR/requirements.txt" ]]; then
        sudo -u "$APP_USER" "$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"
    fi
    
    log_success "Python environment ready"
}

step_setup_systemd() {
    log_info "Step 6: Setting up systemd service..."
    
    cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=ButterflyFX Dimensional Server
After=network.target

[Service]
Type=simple
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/python ${APP_DIR}/server/dimensional_server.py --port ${PORT} --static ${APP_DIR}/web --data ${APP_DIR}/data
Restart=always
RestartSec=5
StandardOutput=append:${APP_DIR}/logs/server.log
StandardError=append:${APP_DIR}/logs/error.log

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=${APP_DIR}/data ${APP_DIR}/logs
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable ${APP_NAME}
    
    log_success "Systemd service configured"
}

step_setup_nginx() {
    log_info "Step 7: Setting up nginx..."
    
    # Create nginx config
    cat > /etc/nginx/sites-available/${APP_NAME} << EOF
server {
    listen 80;
    server_name ${DOMAIN};
    
    # Logging
    access_log /var/log/nginx/${APP_NAME}_access.log;
    error_log /var/log/nginx/${APP_NAME}_error.log;
    
    # Proxy to dimensional server
    location / {
        proxy_pass http://127.0.0.1:${PORT};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # WebSocket support
        proxy_read_timeout 86400;
    }
    
    # Static files with caching
    location /static/ {
        alias ${APP_DIR}/web/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:${PORT}/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
    
    # Manifold protocol
    location /manifold/ {
        proxy_pass http://127.0.0.1:${PORT}/manifold/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

    # Enable site
    ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test config
    nginx -t
    
    log_success "Nginx configured"
}

step_setup_ssl() {
    log_info "Step 8: Setting up SSL with Let's Encrypt..."
    
    if [[ -z "$DOMAIN" ]]; then
        log_error "Domain required for SSL"
        return 1
    fi
    
    # Install certbot
    apt-get install -y -qq certbot python3-certbot-nginx
    
    # Get certificate
    if [[ -n "$SSL_EMAIL" ]]; then
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$SSL_EMAIL"
    else
        certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email
    fi
    
    # Setup auto-renewal
    systemctl enable certbot.timer
    systemctl start certbot.timer
    
    log_success "SSL configured"
}

step_setup_firewall() {
    log_info "Step 9: Configuring firewall..."
    
    # Enable UFW
    ufw --force enable
    
    # Allow SSH (important!)
    ufw allow ssh
    
    # Allow HTTP/HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp
    
    # Allow direct port if not using nginx
    if [[ "$USE_NGINX" != true ]]; then
        ufw allow ${PORT}/tcp
    fi
    
    log_success "Firewall configured"
}

step_start_services() {
    log_info "Step 10: Starting services..."
    
    # Start dimensional server
    systemctl start ${APP_NAME}
    
    # Start/reload nginx if used
    if [[ "$USE_NGINX" == true ]]; then
        systemctl reload nginx
    fi
    
    # Wait a moment
    sleep 2
    
    # Check status
    if systemctl is-active --quiet ${APP_NAME}; then
        log_success "Dimensional server is running"
    else
        log_error "Failed to start server"
        journalctl -u ${APP_NAME} --no-pager -n 20
    fi
}

print_success() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                    DEPLOYMENT COMPLETE!                        ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    if [[ "$USE_NGINX" == true && -n "$DOMAIN" ]]; then
        if [[ "$USE_SSL" == true ]]; then
            echo "  🌐 Server URL: https://${DOMAIN}/"
        else
            echo "  🌐 Server URL: http://${DOMAIN}/"
        fi
    else
        IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
        echo "  🌐 Server URL: http://${IP}:${PORT}/"
    fi
    
    echo ""
    echo "  📁 Application directory: ${APP_DIR}"
    echo "  📝 Logs: ${APP_DIR}/logs/"
    echo ""
    echo "  Useful commands:"
    echo "    sudo systemctl status ${APP_NAME}     # Check status"
    echo "    sudo systemctl restart ${APP_NAME}    # Restart server"
    echo "    sudo journalctl -u ${APP_NAME} -f     # View logs"
    echo "    sudo tail -f ${APP_DIR}/logs/server.log"
    echo ""
    echo "  API Endpoints:"
    echo "    GET  /api/status      # Server status"
    echo "    GET  /api/demos       # List demos"
    echo "    GET  /api/content     # List content"
    echo "    GET  /manifold/...    # Manifold protocol"
    echo ""
}

# =============================================================================
# RUN
# =============================================================================

main "$@"
