import boto3
class S3Service:

    async def upload_file(
        self,
        file,
        s3_key
    ):

        print(
            f"Uploading to S3: {s3_key}"
        )

        return {
            "success": True,
            "s3_key": s3_key
        }


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

