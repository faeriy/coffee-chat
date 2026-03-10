import boto3
from app.config import settings
from botocore.exceptions import ClientError

s3_client: boto3.client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)


async def upload_file_to_s3(
    file_content: bytes, file_name: str, content_type: str
) -> str:
    """Upload a file to S3 and return the URL"""
    try:
        url: str = s3_client.put_object()
    except ClientError as e:
        raise Exception(f"Failed to upload file to S3: {str(e)}")
