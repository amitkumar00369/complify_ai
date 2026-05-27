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