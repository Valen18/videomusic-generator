#!/bin/bash
# Complete deployment script for VideoMusic Generator
# Run this on your Ubuntu server with Dokploy

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VideoMusic Generator - Deployment${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo ""
    echo "Create .env file from .env.template:"
    echo "  cp .env.template .env"
    echo "  nano .env"
    echo ""
    echo "Required variables:"
    echo "  - DOCKER_USERNAME"
    echo "  - SUNO_API_KEY"
    echo "  - SESSION_SECRET_KEY"
    exit 1
fi

# Load .env
source .env

# Verify required variables
if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${RED}ERROR: DOCKER_USERNAME not set in .env${NC}"
    exit 1
fi

if [ -z "$SUNO_API_KEY" ]; then
    echo -e "${RED}ERROR: SUNO_API_KEY not set in .env${NC}"
    exit 1
fi

if [ -z "$SESSION_SECRET_KEY" ]; then
    echo -e "${RED}ERROR: SESSION_SECRET_KEY not set in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Environment variables loaded${NC}"
echo ""

# Pull latest image
echo -e "${GREEN}Pulling latest image from Docker Hub...${NC}"
docker-compose pull

# Stop existing containers
if docker ps -a | grep -q videomusic-generator; then
    echo -e "${YELLOW}Stopping existing containers...${NC}"
    docker-compose down
fi

# Start containers
echo -e "${GREEN}Starting containers...${NC}"
docker-compose up -d

# Wait for health check
echo -e "${YELLOW}Waiting for application to start...${NC}"
sleep 10

# Check health
echo -e "${GREEN}Checking application health...${NC}"
HEALTH=$(curl -s http://localhost:${HOST_PORT:-8000}/health || echo "failed")

if [[ $HEALTH == *"healthy"* ]]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ DEPLOYMENT SUCCESSFUL!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Application is running at:"
    echo "  http://localhost:${HOST_PORT:-8000}"
    echo ""
    echo "View logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "Stop application:"
    echo "  docker-compose down"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}✗ DEPLOYMENT FAILED${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    echo "Check logs with:"
    echo "  docker-compose logs"
    exit 1
fi
