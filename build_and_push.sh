#!/bin/bash
# Docker build and push script

set -e

IMAGE_NAME="ecommerce-personalization"
REGISTRY="your-registry"
TAG="latest"

echo "Building Docker image..."
docker build -t $IMAGE_NAME:$TAG .

echo "Tagging image for registry..."
docker tag $IMAGE_NAME:$TAG $REGISTRY/$IMAGE_NAME:$TAG

echo "Pushing to registry..."
docker push $REGISTRY/$IMAGE_NAME:$TAG

echo "✅ Image pushed to $REGISTRY/$IMAGE_NAME:$TAG"
