
import os

from app.services.s3_service import (
    s3_client
)

from core.config import settings


class S3StorageService:

    # ==========================================
    # UPLOAD FILE
    # ==========================================
    @staticmethod
    async def upload_file(
        local_path,
        s3_key
    ):

        s3_client.upload_file(
            local_path,
            settings.AWS_BUCKET_NAME,
            s3_key
        )

        return s3_key

    # ==========================================
    # DOWNLOAD FILE
    # ==========================================
    @staticmethod
    async def download_file(
        s3_key,
        local_path
    ):

        os.makedirs(
            os.path.dirname(local_path),
            exist_ok=True
        )

        s3_client.download_file(
            settings.AWS_BUCKET_NAME,
            s3_key,
            local_path
        )

        return local_path

    # ==========================================
    # MOVE FILE
    # ==========================================
    @staticmethod
    async def move_file(
        old_key,
        new_key
    ):

        s3_client.copy_object(
            Bucket=settings.AWS_BUCKET_NAME,
            CopySource={
                "Bucket":
                settings.AWS_BUCKET_NAME,
                "Key":
                old_key
            },
            Key=new_key
        )

        s3_client.delete_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=old_key
        )

        return new_key

    # ==========================================
    # FILE EXISTS
    # ==========================================
    @staticmethod
    async def file_exists(
        s3_key
    ):

        try:

            s3_client.head_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=s3_key
            )

            return True

        except Exception:

            return False

