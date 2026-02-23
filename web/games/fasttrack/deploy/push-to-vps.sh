#!/bin/bash
# =============================================================================
# Fast Track Remote Deployment to VPS
# Deploys to kensgames.com (172.81.62.217)
# =============================================================================

set -e

VPS_IP="172.81.62.217"
VPS_USER="${1:-root}"
DOMAIN="kensgames.com"
REMOTE_DIR="/var/www/kensgames/fasttrack"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HELIX_DIR="/opt/butterflyfx/dimensionsos/helix"

echo "================================================"
echo "Fast Track Remote Deploy"
echo "  VPS: $VPS_IP ($DOMAIN)"
echo "  From: $LOCAL_DIR"
echo "  To: $VPS_USER@$VPS_IP:$REMOTE_DIR"
echo "================================================"

# Create remote directories first
echo ""
echo "[0/5] Creating remote directories..."
ssh "$VPS_USER@$VPS_IP" "mkdir -p $REMOTE_DIR /opt/butterflyfx/dimensionsos /opt/fasttrack-deploy"

# Sync game files to VPS
echo ""
echo "[1/5] Syncing game files..."
rsync -avz --delete \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='*.log' \
    --exclude='.env' \
    -e "ssh" \
    "$LOCAL_DIR/" "$VPS_USER@$VPS_IP:$REMOTE_DIR/"

# Sync helix module for manifold server
echo ""
echo "[2/5] Syncing helix module (ButterflyFX)..."
ssh "$VPS_USER@$VPS_IP" "mkdir -p /opt/butterflyfx/dimensionsos"
rsync -avz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    -e "ssh" \
    "$HELIX_DIR/" "$VPS_USER@$VPS_IP:/opt/butterflyfx/dimensionsos/helix/"

# Sync deploy scripts
echo ""
echo "[3/5] Syncing deployment configs..."
ssh "$VPS_USER@$VPS_IP" "mkdir -p /opt/fasttrack-deploy"
rsync -avz \
    "$LOCAL_DIR/deploy/" \
    -e "ssh" \
    "$VPS_USER@$VPS_IP:/opt/fasttrack-deploy/"

# Install systemd services
echo ""
echo "[4/5] Installing systemd services..."
ssh "$VPS_USER@$VPS_IP" << 'REMOTE_SCRIPT'
    # Copy service files
    cp /opt/fasttrack-deploy/fasttrack-game.service /etc/systemd/system/
    cp /opt/fasttrack-deploy/fasttrack-manifold.service /etc/systemd/system/
    
    # Reload and enable
    systemctl daemon-reload
    systemctl enable fasttrack-game fasttrack-manifold
    
    # Restart services
    systemctl restart fasttrack-game
    systemctl restart fasttrack-manifold
    
    echo "Services status:"
    systemctl status fasttrack-game --no-pager -l || true
    systemctl status fasttrack-manifold --no-pager -l || true
REMOTE_SCRIPT

# Reload nginx
echo ""
echo "[5/6] Reloading nginx..."
ssh "$VPS_USER@$VPS_IP" "nginx -t && systemctl reload nginx"

# Deploy landing page
echo ""
echo "[6/6] Deploying landing page..."
ssh "$VPS_USER@$VPS_IP" "cp /var/www/kensgames/fasttrack/landing/index.html /var/www/kensgames/index.html"

echo ""
echo "================================================"
echo "Deployment complete!"
echo ""
echo "  Landing: https://kensgames.com"
echo "  Game:    https://kensgames.com/fasttrack"
echo "  Manifold: wss://kensgames.com/manifold"
echo ""
echo "To check logs:"
echo "  ssh $VPS_USER@$VPS_IP journalctl -u fasttrack-game -f"
echo "================================================"
