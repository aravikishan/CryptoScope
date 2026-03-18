FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create instance directory for SQLite
RUN mkdir -p instance

EXPOSE 8010

# Use gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8010", "--workers", "2", "--timeout", "120", "app:create_app()"]
