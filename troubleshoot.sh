#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Spotipie Troubleshooting Script ===${NC}"

# Load environment variables
if [ -f .env ]; then
  echo -e "${GREEN}Loading environment variables from .env file...${NC}"
  source .env
else
  echo -e "${RED}Error: .env file not found.${NC}"
  exit 1
fi

echo -e "${BLUE}Checking Docker services...${NC}"
docker ps -a | grep spotipie

echo -e "${BLUE}Checking Docker network...${NC}"
docker network ls | grep spotipie

echo -e "${BLUE}Checking Docker logs for PostgreSQL...${NC}"
docker logs spotipie-postgres | tail -n 20

echo -e "${BLUE}Checking Docker logs for Spotipie bot...${NC}"
docker logs spotipie-bot | tail -n 20

echo -e "${BLUE}Testing PostgreSQL connection from host...${NC}"
if command -v psql &> /dev/null; then
  PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 'Connection from host successful';" || {
    echo -e "${RED}Failed to connect to PostgreSQL from host.${NC}"
  }
else
  echo -e "${YELLOW}PostgreSQL client not installed on host. Skipping connection test.${NC}"
fi

echo -e "${BLUE}Testing PostgreSQL connection from within the container...${NC}"
docker exec -it spotipie-bot bash -c "PGPASSWORD=$POSTGRES_PASSWORD psql -h postgres -U $POSTGRES_USER -d $POSTGRES_DB -c \"SELECT 'Connection from container successful';\""

echo -e "${BLUE}=== Troubleshooting Recommendations ===${NC}"
echo -e "1. If PostgreSQL is not starting: ${YELLOW}docker-compose up -d postgres${NC}"
echo -e "2. If you need to rebuild the images: ${YELLOW}docker-compose build --no-cache${NC}"
echo -e "3. If you need to reset everything: ${YELLOW}docker-compose down -v && docker-compose up -d${NC}"
echo -e "4. For more detailed logs: ${YELLOW}docker-compose logs -f${NC}" 