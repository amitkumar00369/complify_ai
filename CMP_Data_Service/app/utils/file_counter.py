
import zipfile


class FileCounter:

    @staticmethod
    def count_valid_files(
        zip_path
    ):

        valid_extensions = (

            ".pdf",

            ".doc",

            ".docx",

            ".xlsx",

            ".xls",

            ".csv",

            ".png",

            ".jpg",

            ".jpeg"
        )

        total_files = 0

        try:

            with zipfile.ZipFile(
                zip_path,
                "r"
            ) as zip_ref:

                for name in zip_ref.namelist():

                    if (
                        name.lower().endswith(
                            valid_extensions
                        )
                    ):

                        total_files += 1

        except zipfile.BadZipFile:

            raise Exception(
                "Invalid ZIP file"
            )

        return total_files

