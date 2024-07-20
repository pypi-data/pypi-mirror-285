import boto3

from pureml.utils.logger import get_logger

from ..provider import StorageProvider

logger = get_logger("sdk.storage.cloudflare")


class R2StorageProvider(StorageProvider):
    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        bucket_name: str,
        account_id: str,
        public_url: str,
        bucket_location: str = None,
    ):
        self.r2 = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=access_key_secret,
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        )
        self.bucket_name = bucket_name
        if public_url:
            self.public_url = public_url
        else:
            print("Public URL not found in Cloudflare secrets")

    def upload_file(self, source_file, destination) -> str or None:
        destination = destination.lstrip("/")
        # print(f"Destination: {destination}")
        try:
            self.r2.upload_file(source_file, self.bucket_name, destination)
            self.public_url + "/" + destination
            # print(f"R2 URL :{url}")
            return self.public_url + "/" + destination
        except Exception as e:
            logger.error("Error uploading file to R2", error=e)
            print(e)
            return None

    def download_file(self, source, destination_file):
        source = source.lstrip("/")
        try:
            self.r2.download_file(self.bucket_name, source, destination_file)
        except Exception as e:
            logger.error("Error downloading file from R2", error=e)
            print(e)
