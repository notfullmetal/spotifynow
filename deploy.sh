#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Spotipie Deployment Script ===${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
  echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
  
  if [ ! -f .env.example ]; then
    echo -e "${RED}Error: .env.example file not found. Please create a .env file manually.${NC}"
    exit 1
  fi
  
  cp .env.example .env
  echo -e "${GREEN}Created .env file. Please edit it with your credentials before continuing.${NC}"
  echo -e "${YELLOW}Press Enter to open the file for editing, or Ctrl+C to abort${NC}"
  read
  
  ${EDITOR:-nano} .env
fi

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

echo -e "${BLUE}Pulling latest changes...${NC}"
git pull

echo -e "${BLUE}Making scripts executable...${NC}"
chmod +x init-db.sh docker-entrypoint.sh troubleshoot.sh

echo -e "${BLUE}Building and starting Spotipie...${NC}"
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Check if services are running
if docker ps | grep -q "spotipie-postgres" && docker ps | grep -q "spotipie-bot"; then
  echo -e "${GREEN}Spotipie services are now running!${NC}"
else
  echo -e "${RED}Something went wrong. Some services may not be running.${NC}"
  echo -e "${YELLOW}Run ./troubleshoot.sh to diagnose the issue.${NC}"
fi

echo -e "${BLUE}=== Deployment Complete ===${NC}"
echo -e "${BLUE}To view logs:${NC} docker-compose logs -f"
echo -e "${BLUE}To stop:${NC} docker-compose down"
echo -e "${BLUE}To troubleshoot:${NC} ./troubleshoot.sh" 