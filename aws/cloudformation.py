"""
AWS CloudFormation Template for Serverless Deployment
Defines infrastructure for Lambda, API Gateway, S3, and other services
"""

template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Description": "AI E-commerce Personalization Platform - Serverless Infrastructure",
    "Parameters": {
        "Environment": {
            "Type": "String",
            "Default": "dev",
            "AllowedValues": ["dev", "staging", "prod"]
        },
        "S3BucketName": {
            "Type": "String",
            "Default": "ecommerce-personalization"
        }
    },
    "Resources": {
        "S3Bucket": {
            "Type": "AWS::S3::Bucket",
            "Properties": {
                "BucketName": {"Ref": "S3BucketName"},
                "VersioningConfiguration": {
                    "Status": "Enabled"
                },
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True
                }
            }
        },
        "LambdaExecutionRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                },
                "ManagedPolicyArns": [
                    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                    "arn:aws:iam::aws:policy/AmazonS3FullAccess"
                ]
            }
        },
        "ApiGateway": {
            "Type": "AWS::ApiGateway::RestApi",
            "Properties": {
                "Name": "EcommercePersonalizationAPI",
                "Description": "API for AI-powered recommendations"
            }
        }
    },
    "Outputs": {
        "S3BucketName": {
            "Value": {"Ref": "S3Bucket"},
            "Description": "S3 Bucket for product data storage"
        },
        "ApiGatewayUrl": {
            "Value": {"Fn::Sub": "https://${ApiGateway}.execute-api.${AWS::Region}.amazonaws.com/prod"},
            "Description": "API Gateway endpoint URL"
        }
    }
}


if __name__ == "__main__":
    import json
    print(json.dumps(template, indent=2))
