#!/usr/bin/env python3
import requests
import json
import time
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('cloudflare-ddns')

# Configuration from environment variables (for Docker)
ZONE_ID = os.environ.get('CLOUDFLARE_ZONE_ID')
AUTH_EMAIL = os.environ.get('CLOUDFLARE_AUTH_EMAIL')
AUTH_KEY = os.environ.get('CLOUDFLARE_AUTH_KEY')
DOMAIN_NAME = os.environ.get('DOMAIN_NAME')
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', 3600))  # Default: 1 hour in seconds

# Cloudflare API URLs
LIST_DNS_RECORDS_URL = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}/dns_records"

# Headers for API requests
HEADERS = {
    'X-Auth-Email': AUTH_EMAIL,
    'X-Auth-Key': AUTH_KEY,
    'Content-Type': 'application/json'
}

def get_current_ip():
    """Get the current public IP address of the machine."""
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        response.raise_for_status()
        return response.json()['ip']
    except requests.RequestException as e:
        logger.error(f"Error getting current IP: {e}")
        return None

def get_dns_records():
    """Get DNS records from Cloudflare."""
    try:
        response = requests.get(LIST_DNS_RECORDS_URL, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error getting DNS records: {e}")
        return None

def find_a_record(records, domain_name):
    """Find the A record for the specified domain."""
    if not records or 'result' not in records:
        return None
    
    for record in records['result']:
        if record['type'] == 'A' and record['name'] == domain_name:
            return record
    
    return None

def update_dns_record(record_id, ip_address):
    """Update the DNS A record with the new IP address."""
    update_url = f"{LIST_DNS_RECORDS_URL}/{record_id}"
    
    data = {
        "comment": f"Dynamic DNS Update at {datetime.utcnow().isoformat()}",
        "content": ip_address,
        "name": DOMAIN_NAME,
        "proxied": False,
        "type": "A"
    }
    
    try:
        response = requests.put(update_url, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error updating DNS record: {e}")
        return None

def create_dns_record(ip_address):
    """Create a new DNS A record if it doesn't exist."""
    data = {
        "comment": f"Dynamic DNS Update at {datetime.utcnow().isoformat()}",
        "content": ip_address,
        "name": DOMAIN_NAME,
        "proxied": False,
        "type": "A",
        "ttl": 1
    }
    
    try:
        response = requests.post(LIST_DNS_RECORDS_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error creating DNS record: {e}")
        return None

def update_dynamic_dns():
    """Main function to update dynamic DNS."""
    # Get current IP address
    current_ip = get_current_ip()
    if not current_ip:
        logger.error("Failed to obtain current IP address")
        return False
    
    logger.info(f"Current IP address: {current_ip}")
    
    # Get DNS records
    dns_records = get_dns_records()
    if not dns_records:
        logger.error("Failed to obtain DNS records")
        return False
    
    # Find the A record
    a_record = find_a_record(dns_records, DOMAIN_NAME)
    
    if a_record:
        record_id = a_record['id']
        record_ip = a_record['content']
        
        logger.info(f"Found existing A record with ID: {record_id} and IP: {record_ip}")
        
        # Update only if IP has changed
        if record_ip != current_ip:
            logger.info(f"IP address has changed: {record_ip} -> {current_ip}, updating...")
            result = update_dns_record(record_id, current_ip)
            if result and result.get('success'):
                logger.info(f"Successfully updated DNS record to {current_ip}")
                return True
            else:
                logger.error("Failed to update DNS record")
                return False
        else:
            logger.info("IP address hasn't changed, no update needed")
            return True
    else:
        logger.info(f"No A record found for {DOMAIN_NAME}, creating a new one...")
        result = create_dns_record(current_ip)
        if result and result.get('success'):
            logger.info(f"Successfully created new DNS record with IP {current_ip}")
            return True
        else:
            logger.error("Failed to create DNS record")
            return False

def main():
    """Main execution loop."""
    logger.info("Starting Cloudflare Dynamic DNS updater")
    logger.info(f"Domain: {DOMAIN_NAME}")
    logger.info(f"Update interval: {UPDATE_INTERVAL} seconds")
    
    while True:
        try:
            logger.info("Running DNS update...")
            update_dynamic_dns()
        except Exception as e:
            logger.error(f"Unexpected error during update: {e}")
        
        logger.info(f"Sleeping for {UPDATE_INTERVAL} seconds...")
        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
