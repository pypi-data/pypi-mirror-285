import boto3

from pureml.utils.logger import get_logger

from ..provider import StorageProvider

logger = get_logger("sdk.storage.aws")


class S3StorageProvider(StorageProvider):
    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        bucket_name: str,
        bucket_location: str,
        public_url: str = None,
        account_id: str = None,
    ):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key_secret,
            region_name=bucket_location,
        )
        self.bucket_name = bucket_name
        if public_url:
            self.public_url = public_url
        else:
            self.public_url = (
                f"https://{bucket_name}.s3.{bucket_location}.amazonaws.com"
            )

    def upload_file(self, source_file, destination) -> str or None:
        destination = destination.lstrip("/")
        try:
            self.s3.upload_file(source_file, self.bucket_name, destination)
            return self.public_url + "/" + destination
        except Exception as e:
            logger.error("Error uploading file to S3", error=e)
            print(e)
            return None

    def download_file(self, source, destination_file):
        source = source.lstrip("/")
        try:
            self.s3.download_file(self.bucket_name, source, destination_file)
        except Exception as e:
            logger.error("Error downloading file from S3", error=e)
            print(e)
