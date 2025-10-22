#!/bin/bash
# Build script for VideoMusic Generator Docker image

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VideoMusic Generator - Docker Build${NC}"
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

echo -e "${GREEN}Building image: ${IMAGE_TAG}${NC}"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Build the image
echo -e "${GREEN}Step 1/2: Building Docker image...${NC}"
docker build \
    -f road_to_production/Dockerfile \
    -t ${IMAGE_TAG} \
    -t ${IMAGE_NAME}:latest \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Build successful!${NC}"
    echo ""
    echo -e "${GREEN}Image created:${NC}"
    echo "  - ${IMAGE_TAG}"
    echo "  - ${IMAGE_NAME}:latest"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Test locally: docker run -p 8000:8000 -e SUNO_API_KEY=your-key ${IMAGE_TAG}"
    echo "  2. Push to Docker Hub: ./push.sh"
else
    echo ""
    echo -e "${RED}✗ Build failed!${NC}"
    exit 1
fi
