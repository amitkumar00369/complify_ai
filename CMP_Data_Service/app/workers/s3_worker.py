
import json
import time

from app.services.s3_service import (
    sqs_client
)

from core.config import (
    settings
)

from app.workers.parent_worker import (
    process_parent_zip
)

from app.workers.child_worker import (
    process_child_file
)


def worker_loop():

    print("SQS Worker Started")

    while True:

        response = (
            sqs_client.receive_message(
                QueueUrl=settings.SQS_QUEUE_URL,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=20
            )
        )

        messages = response.get(
            "Messages",
            []
        )

        if not messages:

            continue

        for msg in messages:

            try:

                body = json.loads(
                    msg["Body"]
                )

                records = body.get(
                    "Records",
                    []
                )

                for record in records:

                    bucket = record[
                        "s3"
                    ]["bucket"]["name"]

                    key = record[
                        "s3"
                    ]["object"]["key"]

                    module = key.split("/")[0]

                    filename = key.split("/")[-1]

                    # ==========================
                    # ZIP FILE
                    # ==========================
                    if filename.lower().endswith(
                        ".zip"
                    ):

                        parent_job_id = (
                            filename
                        )

                        process_parent_zip(
                            parent_job_id,
                            module,
                            key
                        )

                    # ==========================
                    # NORMAL FILE
                    # ==========================
                    else:

                        process_child_file(
                            None,
                            None,
                            module,
                            key,
                            filename
                        )

                # ==============================
                # DELETE MESSAGE
                # ==============================
                sqs_client.delete_message(
                    QueueUrl=
                    settings.SQS_QUEUE_URL,

                    ReceiptHandle=
                    msg["ReceiptHandle"]
                )

            except Exception as e:

                print(
                    "SQS Worker Error:",
                    str(e)
                )

        time.sleep(1)


if __name__ == "__main__":

    worker_loop()

