import boto3
import uuid
from core.config import settings


class S3Service:

    def __init__(self):
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