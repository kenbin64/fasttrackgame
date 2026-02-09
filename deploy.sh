#!/bin/bash
# ButterflyFx VPS Deployment Script
# Usage: ./deploy.sh [environment]
# Example: ./deploy.sh production

set -e  # Exit on error

# Configuration
ENVIRONMENT=${1:-production}
REPO_URL="https://github.com/kenbin64/dimensionsos.git"
DEPLOY_DIR="/opt/butterflyfx"
BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}ButterflyFx Deployment Script${NC}"
echo -e "${GREEN}Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}Docker installed successfully${NC}"
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}Docker Compose installed successfully${NC}"
fi

# Create deployment directory
echo -e "${YELLOW}Setting up deployment directory...${NC}"
mkdir -p ${DEPLOY_DIR}
cd ${DEPLOY_DIR}

# Clone or update repository
if [ -d ".git" ]; then
    echo -e "${YELLOW}Updating repository...${NC}"
    git fetch origin
    git reset --hard origin/${BRANCH}
    git pull origin ${BRANCH}
else
    echo -e "${YELLOW}Cloning repository...${NC}"
    git clone -b ${BRANCH} ${REPO_URL} .
fi

# Stop existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker-compose down || true

# Remove old images (optional - saves space)
echo -e "${YELLOW}Cleaning up old images...${NC}"
docker image prune -f

# Build new image
echo -e "${YELLOW}Building Docker image...${NC}"
docker-compose build --no-cache

# Start containers
echo -e "${YELLOW}Starting containers...${NC}"
if [ "${ENVIRONMENT}" == "production" ]; then
    # Production: More workers, optimized settings
    WORKERS=17 docker-compose up -d
else
    # Development/Staging: Fewer workers
    WORKERS=4 docker-compose up -d
fi

# Wait for health check
echo -e "${YELLOW}Waiting for service to be healthy...${NC}"
sleep 10

# Check health
HEALTH_CHECK=$(curl -s http://localhost:8000/api/v1/health || echo "FAILED")
if [[ $HEALTH_CHECK == *"healthy"* ]]; then
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment successful!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Service is running at: http://localhost:8000${NC}"
    echo -e "${GREEN}API Documentation: http://localhost:8000/api/v1/docs${NC}"
    echo -e "${GREEN}Health Check: http://localhost:8000/api/v1/health${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Deployment failed - health check failed${NC}"
    echo -e "${RED}========================================${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker-compose logs --tail=50
    exit 1
fi

# Show running containers
echo -e "${YELLOW}Running containers:${NC}"
docker-compose ps

# Show logs
echo -e "${YELLOW}Recent logs:${NC}"
docker-compose logs --tail=20

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo "  View logs:        docker-compose logs -f"
echo "  Restart:          docker-compose restart"
echo "  Stop:             docker-compose down"
echo "  Check metrics:    curl http://localhost:8000/api/v1/metrics"
echo ""

