FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script
COPY dynamic_dns_updater.py .

# Make script executable
RUN chmod +x dynamic_dns_updater.py

# Run the script
CMD ["python", "dynamic_dns_updater.py"]
