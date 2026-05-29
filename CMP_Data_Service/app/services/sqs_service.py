import json
import boto3

from core.config import settings


class SQSService:

    def __init__(self):

        self.client = boto3.client(
            "sqs",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    def publish_document_uploaded(
        self,
        payload: dict
    ):

        self.client.send_message(
            QueueUrl=settings.SQS_QUEUE_URL,
            MessageBody=json.dumps(payload)
        )


sqs_service = SQSService()