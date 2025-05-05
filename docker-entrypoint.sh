#!/bin/bash
set -e

# Function to check if PostgreSQL is ready
wait_for_postgres() {
  echo "Waiting for PostgreSQL to become available..."
  
  # Wait for PostgreSQL to become available
  # Add timeout to prevent infinite loop
  TIMEOUT=60
  COUNT=0
  until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping (attempt $COUNT/$TIMEOUT)"
    sleep 1
    
    COUNT=$((COUNT+1))
    if [ $COUNT -ge $TIMEOUT ]; then
      echo "ERROR: Timed out waiting for PostgreSQL. Check your connection settings:"
      echo "  POSTGRES_HOST=$POSTGRES_HOST"
      echo "  POSTGRES_USER=$POSTGRES_USER"
      echo "  POSTGRES_DB=$POSTGRES_DB"
      echo "  POSTGRES_PORT=$POSTGRES_PORT"
      echo "You may need to check if PostgreSQL is running and accessible."
      exit 1
    fi
  done
  
  echo "PostgreSQL is up - continuing"
}

# Check if all required environment variables are set
if [ -z "$POSTGRES_HOST" ] || [ -z "$POSTGRES_USER" ] || [ -z "$POSTGRES_PASSWORD" ] || [ -z "$POSTGRES_DB" ]; then
  echo "ERROR: Required PostgreSQL environment variables are not set:"
  echo "  POSTGRES_HOST=${POSTGRES_HOST:-not set}"
  echo "  POSTGRES_USER=${POSTGRES_USER:-not set}"
  echo "  POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-not set}"
  echo "  POSTGRES_DB=${POSTGRES_DB:-not set}"
  exit 1
fi

# Wait for PostgreSQL if database host is defined
wait_for_postgres

# Check if JSON_BLOB_ID is set
if [ -z "$JSON_BLOB_ID" ]; then
  echo "WARNING: JSON_BLOB_ID environment variable is not set. Authentication might not work properly."
fi

# Database connectivity test
echo "Testing database connection..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 'Database connection successful';" || {
  echo "ERROR: Failed to connect to PostgreSQL database after initial connection check."
  exit 1
}

echo "Starting Spotipie Bot..."
# Execute the command passed to the script
exec "$@" 