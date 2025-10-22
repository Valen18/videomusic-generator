#!/bin/bash
# Push script for VideoMusic Generator Docker image

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VideoMusic Generator - Docker Push${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Get Docker username
if [ -z "$DOCKER_USERNAME" ]; then
    echo -e "${YELLOW}Enter your Docker Hub username:${NC}"
    read DOCKER_USERNAME
    export DOCKER_USERNAME
fi

# Get version
if [ -z "$VERSION" ]; then
    VERSION="latest"
fi

IMAGE_NAME="${DOCKER_USERNAME}/videomusic-generator"
IMAGE_TAG="${IMAGE_NAME}:${VERSION}"

echo -e "${GREEN}Pushing image: ${IMAGE_TAG}${NC}"
echo ""

# Check if logged in to Docker Hub
echo -e "${GREEN}Checking Docker Hub login...${NC}"
if ! docker info | grep -q "Username"; then
    echo -e "${YELLOW}Please login to Docker Hub:${NC}"
    docker login
fi

# Push the image
echo ""
echo -e "${GREEN}Pushing version: ${VERSION}${NC}"
docker push ${IMAGE_TAG}

if [ "$VERSION" != "latest" ]; then
    echo ""
    echo -e "${GREEN}Pushing latest tag...${NC}"
    docker push ${IMAGE_NAME}:latest
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Push successful!${NC}"
    echo ""
    echo -e "${GREEN}Your image is now available at:${NC}"
    echo "  https://hub.docker.com/r/${DOCKER_USERNAME}/videomusic-generator"
    echo ""
    echo -e "${GREEN}Pull command:${NC}"
    echo "  docker pull ${IMAGE_TAG}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Deploy with docker-compose on your server"
    echo "  2. See deployment-guide.md for details"
else
    echo ""
    echo -e "${RED}✗ Push failed!${NC}"
    exit 1
fi
