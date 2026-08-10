#!/usr/bin/env bash
set -e

echo "⚡ AETHERIS-WEBFORGE GCP Production Deployer"
echo "================================================"

if [ -z "$1" ]; then
  echo "Usage: ./deploy_gcp.sh <YOUR_GCP_PROJECT_ID> [BUCKET_NAME] [REGION]"
  exit 1
fi

GCP_PROJECT_ID="$1"
BUCKET_NAME="${2:-$1-aetheris-webapp}"
REGION="${3:-asia-south1}"

gcloud config set project "$GCP_PROJECT_ID"
gcloud services enable run.googleapis.com storage.googleapis.com artifactregistry.googleapis.com

if ! gsutil ls -b "gs://$BUCKET_NAME" > /dev/null 2>&1; then
    gsutil mb -l "$REGION" "gs://$BUCKET_NAME"
fi

gsutil iam ch allUsers:objectViewer "gs://$BUCKET_NAME"
gsutil web set -m index.html -e 404.html "gs://$BUCKET_NAME"

gcloud builds submit --tag "gcr.io/$GCP_PROJECT_ID/aetheris-webforge"

gcloud run deploy aetheris-webforge \
    --image "gcr.io/$GCP_PROJECT_ID/aetheris-webforge" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 7860 \
    --memory 2Gi

echo "🎉 DEPLOYMENT COMPLETE! Storage URL: http://$BUCKET_NAME.storage.googleapis.com"
