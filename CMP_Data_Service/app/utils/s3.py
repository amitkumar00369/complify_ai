from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import boto3  # for type checkers / linters
else:
    try:
        import boto3
    except ImportError:
        boto3 = None  # type: ignore
import uuid
from core.config import settings


class S3Service:

    def __init__(self):
        if boto3 is None:
            raise RuntimeError("boto3 is required for S3Service but is not installed")

        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.AWS_BUCKET_NAME

    def upload_file(self, file, folder="uploads"):
        file_ext = file.filename.split(".")[-1]
        file_name = f"{folder}/{uuid.uuid4()}.{file_ext}"

        self.s3.upload_fileobj(
            file.file,
            self.bucket,
            file_name,
            ExtraArgs={"ContentType": file.content_type}
        )

        return f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{file_name}"


s3_service = S3Service()