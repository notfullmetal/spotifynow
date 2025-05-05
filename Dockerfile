FROM python:3.8.2-slim-buster
LABEL maintainer="Spotipie Team"

# Install PostgreSQL client and other dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Wait for PostgreSQL to be ready before starting the bot
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "sp_bot"]