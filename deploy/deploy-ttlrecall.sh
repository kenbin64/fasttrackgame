#!/bin/bash
#
# Deploy TTL Recall to Production
# 
# Copyright (c) 2024-2026 Kenneth Bingham
# Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
#
# This script deploys the TTL Recall application to production
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_DIR="/var/www/ttlrecall"
SOURCE_DIR="/opt/butterflyfx/dimensionsos"
WEB_DIR="$DEPLOY_DIR/web/ttlrecall"
NGINX_USER="www-data"

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  TTL Recall - Production Deployment                        ║${NC}"
echo -e "${GREEN}║  ButterflyFX AI                                             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Please run as root (sudo)${NC}"
    exit 1
fi

# Step 1: Create deployment directory
echo -e "${YELLOW}[1/5] Creating deployment directory...${NC}"
mkdir -p $WEB_DIR
mkdir -p $DEPLOY_DIR/logs
mkdir -p $DEPLOY_DIR/api

# Step 2: Copy web files
echo -e "${YELLOW}[2/5] Copying web files...${NC}"

# Copy main app files
cp -v $SOURCE_DIR/web/ttlrecall/full-app.html $WEB_DIR/index.html
cp -v $SOURCE_DIR/web/ttlrecall/ai-client.js $WEB_DIR/
cp -v $SOURCE_DIR/web/ttlrecall/app.html $WEB_DIR/

echo -e "${GREEN}✓ Web files copied${NC}"

# Step 3: Set permissions
echo -e "${YELLOW}[3/5] Setting permissions...${NC}"
chown -R $NGINX_USER:$NGINX_USER $DEPLOY_DIR
chmod -R 755 $WEB_DIR
chmod -R 755 $DEPLOY_DIR/logs

echo -e "${GREEN}✓ Permissions set${NC}"

# Step 4: Create API stub (if not exists)
echo -e "${YELLOW}[4/5] Setting up API endpoint...${NC}"

if [ ! -f "$DEPLOY_DIR/api/server.py" ]; then
    cat > $DEPLOY_DIR/api/server.py << 'PYEOF'
#!/usr/bin/env python3
"""
TTL Recall API Server
Handles AI requests with multi-provider support
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import json
import time

app = Flask(__name__)
CORS(app)

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'ttlrecall-api',
        'version': '1.0.0'
    })

# Chat endpoint (stub - integrate with real AI)
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    prompt = data.get('prompt', '')
    
    # TODO: Integrate with OpenAI/Gemini/etc
    response = f"Echo: {prompt}"
    
    return jsonify({
        'response': response,
        'provider': 'stub',
        'cached': False
    })

# Streaming chat endpoint
@app.route('/api/chat/stream', methods=['POST'])
def chat_stream():
    data = request.json
    prompt = data.get('prompt', '')
    
    def generate():
        # TODO: Integrate with real streaming AI
        words = f"Streaming response to: {prompt}".split()
        for word in words:
            yield f"data: {json.dumps({'content': word + ' '})}\n\n"
            time.sleep(0.1)
    
    return Response(generate(), mimetype='text/event-stream')

# Image generation endpoint
@app.route('/api/image/generate', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '')
    
    # TODO: Integrate with DALL-E/Stable Diffusion
    return jsonify({
        'url': 'https://via.placeholder.com/1024x1024?text=Generated+Image',
        'provider': 'stub'
    })

# Video generation endpoint
@app.route('/api/video/generate', methods=['POST'])
def generate_video():
    data = request.json
    prompt = data.get('prompt', '')
    
    # TODO: Integrate with Runway/Pika
    return jsonify({
        'job_id': 'stub-' + str(int(time.time())),
        'status': 'processing'
    })

# Video status endpoint
@app.route('/api/video/status/<job_id>', methods=['GET'])
def video_status(job_id):
    # TODO: Check actual job status
    return jsonify({
        'status': 'completed',
        'url': 'https://www.w3schools.com/html/mov_bbb.mp4',
        'progress': 100
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
PYEOF

    chmod +x $DEPLOY_DIR/api/server.py
    
    # Create systemd service
    cat > /etc/systemd/system/ttlrecall-api.service << 'SVCEOF'
[Unit]
Description=TTL Recall API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/ttlrecall/api
ExecStart=/usr/bin/python3 /var/www/ttlrecall/api/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVCEOF

    # Install Flask if not present
    pip3 install flask flask-cors 2>/dev/null || true
    
    # Enable and start service
    systemctl daemon-reload
    systemctl enable ttlrecall-api
    systemctl restart ttlrecall-api
    
    echo -e "${GREEN}✓ API server configured and started${NC}"
else
    echo -e "${BLUE}API server already exists, restarting...${NC}"
    systemctl restart ttlrecall-api
fi

# Step 5: Verify deployment
echo -e "${YELLOW}[5/5] Verifying deployment...${NC}"

# Check if files exist
if [ -f "$WEB_DIR/index.html" ]; then
    echo -e "${GREEN}✓ index.html deployed${NC}"
else
    echo -e "${RED}✗ index.html missing${NC}"
fi

if [ -f "$WEB_DIR/ai-client.js" ]; then
    echo -e "${GREEN}✓ ai-client.js deployed${NC}"
else
    echo -e "${RED}✗ ai-client.js missing${NC}"
fi

# Check API service
if systemctl is-active --quiet ttlrecall-api; then
    echo -e "${GREEN}✓ API server running${NC}"
else
    echo -e "${RED}✗ API server not running${NC}"
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Deployment Complete!                                       ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Deployment summary:"
echo "  • Web files: $WEB_DIR"
echo "  • API server: http://localhost:8080"
echo "  • Logs: $DEPLOY_DIR/logs"
echo ""
echo "Next steps:"
echo "  1. Run SSL setup: sudo bash $SOURCE_DIR/deploy/setup-ssl-ttlrecall.sh"
echo "  2. Access site: https://ttlrecall.com"
echo ""
echo "API endpoints:"
echo "  • https://ttlrecall.com/api/health"
echo "  • https://ttlrecall.com/api/chat"
echo "  • https://ttlrecall.com/api/image/generate"
echo "  • https://ttlrecall.com/api/video/generate"
echo ""
