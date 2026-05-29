import json
import logging

import aioboto3

from core.config import settings


logger = logging.getLogger(
    __name__
)


class SQSService:

    def __init__(self):

        self.session = (
            aioboto3.Session()
        )

        self.queue_url = (
            settings.SQS_QUEUE_URL
        )

    async def publish_document_uploaded(
        self,
        payload: dict
    ):

        try:

            async with (
                self.session.client(
                    "sqs",
                    aws_access_key_id=
                    settings.AWS_ACCESS_KEY_ID,

                    aws_secret_access_key=
                    settings.AWS_SECRET_ACCESS_KEY,

                    region_name=
                    settings.AWS_REGION
                )
            ) as client:

                response = (
                    await client.send_message(
                        QueueUrl=
                        self.queue_url,

                        MessageBody=
                        json.dumps(
                            payload
                        ),

                        MessageAttributes={
                            "module": {
                                "DataType":
                                "String",

                                "StringValue":
                                payload.get(
                                    "module",
                                    ""
                                )
                            }
                        }
                    )
                )

                logger.info(
                    "SQS Message Published "
                    f"MessageId="
                    f"{response['MessageId']}"
                )

                return response

        except Exception:

            logger.exception(
                "Failed to publish "
                "SQS message"
            )

            raise


sqs_service = SQSService()