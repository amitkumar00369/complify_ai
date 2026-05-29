import json
import time
import signal
import logging

from app.aws.clients import (
    sqs_client
)

from core.config import (
    settings
)

from app.workers.parent_worker_s3 import (
    process_parent_zip
)


logger = logging.getLogger(
    __name__
)

RUNNING = True


def shutdown_handler(
    signum,
    frame
):
    global RUNNING

    logger.info(
        "Stopping SQS Consumer..."
    )

    RUNNING = False


signal.signal(
    signal.SIGINT,
    shutdown_handler
)

signal.signal(
    signal.SIGTERM,
    shutdown_handler
)


def start_consumer():

    logger.info(
        "SQS Consumer Started"
    )

    while RUNNING:

        try:

            response = (
                sqs_client.receive_message(
                    QueueUrl=
                    settings.SQS_QUEUE_URL,

                    MaxNumberOfMessages=10,

                    WaitTimeSeconds=20,

                    VisibilityTimeout=300
                )
            )

            messages = response.get(
                "Messages",
                []
            )

            if not messages:

                continue

            logger.info(
                f"Received "
                f"{len(messages)} "
                f"messages"
            )

            for message in messages:

                try:

                    payload = json.loads(
                        message["Body"]
                    )

                    job_id = payload.get(
                        "job_id"
                    )

                    module = payload.get(
                        "module"
                    )

                    s3_key = payload.get(
                        "s3_key"
                    )

                    if not all(
                        [
                            job_id,
                            module,
                            s3_key
                        ]
                    ):

                        logger.error(
                            f"Invalid Payload: "
                            f"{payload}"
                        )

                        continue

                    task = (
                        process_parent_zip.delay(
                            job_id,
                            module,
                            s3_key
                        )
                    )

                    logger.info(
                        f"Queued Parent Job "
                        f"{job_id} "
                        f"Task={task.id}"
                    )

                    sqs_client.delete_message(
                        QueueUrl=
                        settings.SQS_QUEUE_URL,

                        ReceiptHandle=
                        message[
                            "ReceiptHandle"
                        ]
                    )

                except Exception as e:

                    logger.exception(
                        f"Failed Processing "
                        f"Message: {str(e)}"
                    )

        except Exception as e:

            logger.exception(
                f"SQS Consumer Error: "
                f"{str(e)}"
            )

            time.sleep(5)

    logger.info(
        "SQS Consumer Stopped"
    )