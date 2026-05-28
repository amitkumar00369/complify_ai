import os
import shutil
import boto3

from botocore.exceptions import (
    NoCredentialsError
)

BASE_STORAGE = "storage"


class StorageService:

    def __init__(self):

        self.aws_access_key = os.getenv(
            "AWS_ACCESS_KEY_ID"
        )

        self.aws_secret_key = os.getenv(
            "AWS_SECRET_ACCESS_KEY"
        )

        self.bucket = os.getenv(
            "AWS_BUCKET_NAME"
        )

        self.use_s3 = all([

            self.aws_access_key,

            self.aws_secret_key,

            self.bucket
        ])

        # ==================================
        # INIT S3
        # ==================================
        if self.use_s3:

            self.s3 = boto3.client(
                "s3",
                aws_access_key_id=(
                    self.aws_access_key
                ),
                aws_secret_access_key=(
                    self.aws_secret_key
                )
            )

    # ======================================
    # UPLOAD FILE
    # ======================================
    async def upload_file(
        self,
        local_path,
        module,
        folder,
        file_name
    ):

        storage_key = (
            f"{module}/{folder}/{file_name}"
        )

        # ==================================
        # S3 STORAGE
        # ==================================
        if self.use_s3:

            try:

                self.s3.upload_file(
                    local_path,
                    self.bucket,
                    storage_key
                )

                return storage_key

            except NoCredentialsError:

                pass

        # ==================================
        # LOCAL STORAGE
        # ==================================
        local_storage_path = (
            os.path.join(
                BASE_STORAGE,
                module,
                folder
            )
        )

        os.makedirs(
            local_storage_path,
            exist_ok=True
        )

        destination = os.path.join(
            local_storage_path,
            file_name
        )

        shutil.copy2(
            local_path,
            destination
        )

        return destination

    # ======================================
    # MOVE FILE
    # ======================================
    async def move_file(
        self,
        old_path,
        module,
        new_folder
    ):

        file_name = os.path.basename(
            old_path
        )

        # ==================================
        # S3 MOVE
        # ==================================
        if self.use_s3:

            new_key = (
                f"{module}/{new_folder}/{file_name}"
            )

            self.s3.copy_object(

                Bucket=self.bucket,

                CopySource={
                    "Bucket": self.bucket,
                    "Key": old_path
                },

                Key=new_key
            )

            self.s3.delete_object(

                Bucket=self.bucket,

                Key=old_path
            )

            return new_key

        # ==================================
        # LOCAL MOVE
        # ==================================
        destination_dir = (
            os.path.join(
                BASE_STORAGE,
                module,
                new_folder
            )
        )

        os.makedirs(
            destination_dir,
            exist_ok=True
        )

        destination = os.path.join(
            destination_dir,
            file_name
        )

        shutil.move(
            old_path,
            destination
        )

        return destination

    # ======================================
    # MOVE EXISTING FILE
    # processed -> archived
    # ======================================
    async def move_existing_file(
        self,
        source_path,
        destination_path
    ):

        # ==================================
        # S3 MOVE
        # ==================================
        if self.use_s3:

            self.s3.copy_object(

                Bucket=self.bucket,

                CopySource={
                    "Bucket": self.bucket,
                    "Key": source_path
                },

                Key=destination_path
            )

            self.s3.delete_object(

                Bucket=self.bucket,

                Key=source_path
            )

            return destination_path

        # ==================================
        # LOCAL MOVE
        # ==================================
        os.makedirs(
            os.path.dirname(
                destination_path
            ),
            exist_ok=True
        )

        shutil.move(
            source_path,
            destination_path
        )

        return destination_path


storage_service = StorageService()