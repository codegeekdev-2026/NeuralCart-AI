"""
AWS Integration Services
"""
import logging
from typing import Optional, Dict, Any
import boto3
from app.config import settings
import asyncio
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Service:
    """Service for AWS S3 integration"""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket = settings.S3_BUCKET
    
    def upload_product_data(self, key: str, data: Dict[str, Any]) -> bool:
        """Upload product data to S3"""
        try:
            import json
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(data),
                ContentType='application/json'
            )
            logger.info(f"Uploaded product data to S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return False
    
    def download_product_data(self, key: str) -> Optional[Dict[str, Any]]:
        """Download product data from S3"""
        try:
            import json
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            data = json.loads(response['Body'].read().decode('utf-8'))
            return data
        except ClientError as e:
            logger.error(f"Error downloading from S3: {e}")
            return None
    
    def list_objects(self, prefix: str = '') -> list:
        """List objects in S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            return response.get('Contents', [])
        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            return []


class LambdaService:
    """Service for AWS Lambda integration"""
    
    def __init__(self):
        self.lambda_client = boto3.client(
            'lambda',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    def invoke_function(self, function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke Lambda function"""
        try:
            import json
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            if response['StatusCode'] == 200:
                import json
                response_payload = json.loads(response['Payload'].read())
                return response_payload
            else:
                logger.error(f"Lambda invocation failed with status {response['StatusCode']}")
                return {'error': 'Lambda invocation failed'}
        
        except ClientError as e:
            logger.error(f"Error invoking Lambda: {e}")
            return {'error': str(e)}
    
    def invoke_async(self, function_name: str, payload: Dict[str, Any]) -> bool:
        """Invoke Lambda function asynchronously"""
        try:
            import json
            self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='Event',
                Payload=json.dumps(payload)
            )
            logger.info(f"Invoked Lambda function {function_name} asynchronously")
            return True
        except ClientError as e:
            logger.error(f"Error invoking Lambda: {e}")
            return False


class APIGatewayService:
    """Service for AWS API Gateway integration"""
    
    def __init__(self):
        self.apigw_client = boto3.client(
            'apigateway',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
    
    def get_api_deployments(self, api_id: str) -> list:
        """Get API Gateway deployments"""
        try:
            response = self.apigw_client.get_deployments(restApiId=api_id)
            return response.get('items', [])
        except ClientError as e:
            logger.error(f"Error getting API deployments: {e}")
            return []


# Initialize services
s3_service = S3Service()
lambda_service = LambdaService()
apigw_service = APIGatewayService()
