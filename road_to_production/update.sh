#!/bin/bash
# Auto-update script for VideoMusic Generator
# Run this on the server to pull latest changes and redeploy

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VideoMusic Generator - Update${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

cd ~/videomusic/videomusic-generator

echo -e "${YELLOW}Pulling latest changes from Git...${NC}"
git pull

echo -e "${YELLOW}Stopping containers...${NC}"
cd road_to_production
docker-compose down

echo -e "${YELLOW}Rebuilding image...${NC}"
DOCKER_USERNAME=va360 ./build.sh

echo -e "${YELLOW}Starting containers...${NC}"
docker-compose up -d

echo -e "${YELLOW}Waiting for application to start...${NC}"
sleep 10

echo -e "${GREEN}✓ Update complete!${NC}"
echo ""
echo "View logs: docker-compose logs -f"
echo "Access: http://158.220.94.179:8000"
