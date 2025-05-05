#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create extensions if needed
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- Grant privileges to the user
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
    
    -- Create a test entry to verify connectivity
    CREATE TABLE IF NOT EXISTS db_check (
        id SERIAL PRIMARY KEY,
        message VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    INSERT INTO db_check (message) VALUES ('Database initialization successful');
EOSQL

echo "PostgreSQL database initialized successfully" 