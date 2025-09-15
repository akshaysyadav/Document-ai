from minio import Minio
from minio.error import S3Error
import os
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

# Initialize MinIO client
try:
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE
    )
    logger.info(f"MinIO client initialized with endpoint: {MINIO_ENDPOINT}")
except Exception as e:
    logger.error(f"Failed to initialize MinIO client: {e}")
    minio_client = None

# Bucket configuration
DOCUMENTS_BUCKET = "kmrl-documents"
THUMBNAILS_BUCKET = "kmrl-thumbnails"
PROCESSED_BUCKET = "kmrl-processed"

def create_buckets():
    """Create necessary buckets if they don't exist"""
    try:
        if minio_client is None:
            raise Exception("MinIO client not initialized")
            
        buckets = [DOCUMENTS_BUCKET, THUMBNAILS_BUCKET, PROCESSED_BUCKET]
        
        for bucket_name in buckets:
            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)
                logger.info(f"Created MinIO bucket: {bucket_name}")
            else:
                logger.info(f"MinIO bucket already exists: {bucket_name}")
                
    except S3Error as e:
        logger.error(f"Failed to create MinIO buckets: {e}")
        raise

def upload_file(file_path: str, object_name: str, bucket_name: str = DOCUMENTS_BUCKET):
    """Upload a file to MinIO"""
    try:
        if minio_client is None:
            raise Exception("MinIO client not initialized")
            
        minio_client.fput_object(bucket_name, object_name, file_path)
        logger.info(f"Uploaded file to MinIO: {bucket_name}/{object_name}")
        
        return f"{bucket_name}/{object_name}"
        
    except S3Error as e:
        logger.error(f"Failed to upload file: {e}")
        raise

def download_file(object_name: str, file_path: str, bucket_name: str = DOCUMENTS_BUCKET):
    """Download a file from MinIO"""
    try:
        if minio_client is None:
            raise Exception("MinIO client not initialized")
            
        minio_client.fget_object(bucket_name, object_name, file_path)
        logger.info(f"Downloaded file from MinIO: {bucket_name}/{object_name}")
        
        return file_path
        
    except S3Error as e:
        logger.error(f"Failed to download file: {e}")
        raise

def get_presigned_url(object_name: str, bucket_name: str = DOCUMENTS_BUCKET, expires: timedelta = timedelta(hours=1)):
    """Get a presigned URL for file access"""
    try:
        if minio_client is None:
            raise Exception("MinIO client not initialized")
            
        url = minio_client.presigned_get_object(bucket_name, object_name, expires=expires)
        logger.info(f"Generated presigned URL for: {bucket_name}/{object_name}")
        
        return url
        
    except S3Error as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise

def delete_file(object_name: str, bucket_name: str = DOCUMENTS_BUCKET):
    """Delete a file from MinIO"""
    try:
        if minio_client is None:
            raise Exception("MinIO client not initialized")
            
        minio_client.remove_object(bucket_name, object_name)
        logger.info(f"Deleted file from MinIO: {bucket_name}/{object_name}")
        
    except S3Error as e:
        logger.error(f"Failed to delete file: {e}")
        raise

def list_files(bucket_name: str = DOCUMENTS_BUCKET, prefix: str = ""):
    """List files in a bucket"""
    try:
        if minio_client is None:
            raise Exception("MinIO client not initialized")
            
        objects = minio_client.list_objects(bucket_name, prefix=prefix)
        return [obj.object_name for obj in objects]
        
    except S3Error as e:
        logger.error(f"Failed to list files: {e}")
        raise

# Initialize buckets on module import
if minio_client:
    try:
        create_buckets()
    except Exception as e:
        logger.warning(f"Could not create buckets on startup: {e}")
