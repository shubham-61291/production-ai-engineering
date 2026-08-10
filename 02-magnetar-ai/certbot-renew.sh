#!/bin/sh
set -e

DOMAIN=${DOMAIN:-localhost}
EMAIL=${CERTBOT_EMAIL}

while true; do
  certbot certonly --webroot -w /var/www/certbot --email "$EMAIL" --agree-tos --no-eff-email -d "$DOMAIN" --non-interactive --keep-until-expiring
  sleep 43200
done
