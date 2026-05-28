
from app.services.s3_service import (
    s3_client
)


def move_s3_file(
    bucket,
    old_key,
    new_key
):

    s3_client.copy_object(
        Bucket=bucket,
        CopySource={
            "Bucket": bucket,
            "Key": old_key
        },
        Key=new_key
    )

    s3_client.delete_object(
        Bucket=bucket,
        Key=old_key
    )
