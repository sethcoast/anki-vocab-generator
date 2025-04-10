#!/bin/bash

# Set variables
IMAGE_NAME=gcr.io/anki-vocab-generator/anki-vocab-generator-api-prod:latest
SERVICE_NAME=anki-vocab-api
REGION=us-central1
SECRET_NAME=openai-api-key

echo "📦 Building Docker image..."
docker build --platform=linux/amd64 -t  $IMAGE_NAME .

echo "🚀 Pushing Docker image to Container Registry..."
docker push $IMAGE_NAME

echo "☁️ Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --update-secrets OPENAI_API_KEY=$SECRET_NAME:latest

echo "✅ Deployment complete!"
