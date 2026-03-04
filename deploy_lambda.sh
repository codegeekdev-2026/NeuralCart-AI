#!/bin/bash
# Deployment script for AWS Lambda

set -e

echo "Building Lambda package..."

# Create build directory
mkdir -p build
cd build

# Copy requirements
pip install -r ../requirements.txt -t ./

# Add application code
cp -r ../app .
cp ../aws/lambda_handler.py .

# Create deployment package
zip -r ../lambda_deployment.zip .

cd ..

echo "Lambda package created: lambda_deployment.zip"

# Deploy to AWS Lambda (requires AWS CLI)
if command -v aws &> /dev/null; then
    echo "Deploying to AWS Lambda..."
    aws lambda update-function-code \
        --function-name ecommerce-recommendations \
        --zip-file fileb://lambda_deployment.zip \
        --region us-east-1
    echo "Deployment complete!"
else
    echo "AWS CLI not found. Please install it to deploy to Lambda."
    echo "Upload lambda_deployment.zip manually to AWS Lambda console."
fi

# Cleanup
rm -rf build
