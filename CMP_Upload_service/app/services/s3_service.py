import logging
import boto3
import aioboto3

from core.config import settings


logger = logging.getLogger(
    __name__
)


class S3Service:

    def __init__(self):

        self.session = (
            aioboto3.Session()
        )

        self.bucket_name = (
            settings.AWS_BUCKET_NAME
        )

    async def upload_file(
        self,
        local_file_path: str,
        s3_key: str
    ):

        try:

            async with (
                self.session.client(
                    "s3",
                    aws_access_key_id=
                    settings.AWS_ACCESS_KEY_ID,

                    aws_secret_access_key=
                    settings.AWS_SECRET_ACCESS_KEY,

                    region_name=
                    settings.AWS_REGION
                )
            ) as client:

                with open(
                    local_file_path,
                    "rb"
                ) as file_obj:

                    await client.upload_fileobj(
                        file_obj,
                        self.bucket_name,
                        s3_key
                    )

                logger.info(
                    f"S3 Upload Success: "
                    f"{s3_key}"
                )

                return {
                    "success": True,
                    "s3_key": s3_key
                }

        except Exception:

            logger.exception(
                f"S3 Upload Failed: "
                f"{s3_key}"
            )

            raise

    async def download_file(
        self,
        s3_key: str,
        local_path: str
    ):

        try:

            async with (
                self.session.client(
                    "s3",
                    aws_access_key_id=
                    settings.AWS_ACCESS_KEY_ID,

                    aws_secret_access_key=
                    settings.AWS_SECRET_ACCESS_KEY,

                    region_name=
                    settings.AWS_REGION
                )
            ) as client:

                with open(
                    local_path,
                    "wb"
                ) as file_obj:

                    await client.download_fileobj(
                        self.bucket_name,
                        s3_key,
                        file_obj
                    )

                logger.info(
                    f"S3 Download Success: "
                    f"{s3_key}"
                )

                return local_path

        except Exception:

            logger.exception(
                f"S3 Download Failed: "
                f"{s3_key}"
            )

            raise


s3_service = S3Service()





from core.config import  settings   
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

sqs_client = boto3.client(
    "sqs",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

