# Cloudflare Dynamic DNS Updater

This is a Python-based solution that provides dynamic DNS functionality by automatically updating your Cloudflare DNS records with your current public IP address.

## Features

- Automatically detects and updates your public IP address in Cloudflare DNS
- Updates only when your IP changes
- Creates A record if it doesn't exist
- Runs in a Docker container for easy deployment on Synology NAS
- Configurable via environment variables

## Files

- `dynamic_dns_updater.py`: The main Python script that handles the DNS updates
- `docker-compose.yml`: Configuration for Docker Compose
- `Dockerfile`: Instructions for building the Docker image
- `requirements.txt`: Python dependencies

## Setup Instructions

### 1. Clone or Download the Files

Create a directory on your Synology NAS (via SSH or File Station) and save all the files there.

### 2. Customize Configuration (Optional)

Edit the `docker-compose.yml` file to modify any of these settings:

```yaml
environment:
  - CLOUDFLARE_ZONE_ID={YOUR_DNS_ZONE_ID} # Can be found on the overview page of your cloudflare dashboard
  - CLOUDFLARE_AUTH_EMAIL={YOUR_CF_EMAIL_ADDRESS}
  - CLOUDFLARE_AUTH_KEY={YOUR_CF_GLOBAL_API_KEY}
  - DOMAIN_NAME={YOUR_DOMAIN_NAME} # ex. example.com
  - UPDATE_INTERVAL=3600  # Update every hour (in seconds)
```

### 3. Deploy on Synology NAS

#### Using Docker Compose via SSH

1. SSH into your Synology NAS
2. Navigate to the directory containing the files
3. Run:
   ```
   docker-compose up -d
   ```

#### Using Docker Compose in Synology DSM UI

1. Install Docker and Docker Compose packages on your Synology NAS
2. Open Docker app in DSM
3. Go to "Registry" and search for "python"
4. Download the "python:3.9-slim" image
5. Go to "Project" > "Add" > "Create with Compose"
6. Upload your project folder or paste in the docker-compose.yml
7. Click "Apply" to deploy

### 4. Verify Operation

Check the logs to ensure everything is working correctly:

```
docker logs cloudflare-ddns
```

## Security Considerations

- The current configuration includes your Cloudflare API key directly in the docker-compose.yml file. For improved security, consider:
  - Using Docker secrets or environment files
  - Creating a dedicated API token in Cloudflare with limited permissions instead of using the Global API Key

## Troubleshooting

- If the container isn't updating DNS records:
  - Check the logs: `docker logs cloudflare-ddns`
  - Verify your Cloudflare credentials are correct
  - Check that your domain and zone ID are correct
  - Ensure your Synology NAS has internet access

## License

This project is available for your use and modification.
