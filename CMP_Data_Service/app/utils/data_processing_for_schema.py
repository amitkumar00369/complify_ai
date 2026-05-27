from typing import List, Dict
class ResponseBuilder:

    @staticmethod
    async def buildResponseOfProduct(data):

        try:

            if not data:
                return {}

            first_item = data[0]

            result = {
                "caseId": first_item.get("caseId"),
                "pcocData": first_item.get("pcocData"),
                "standard_name": first_item.get("standard_name"),
                "modelName": first_item.get("modelName"),
                "product_name": first_item.get("product_name"),
                "folder_name": first_item.get("folder_name"),
                "hsCode_4": first_item.get("hsCode_4"),
                "hs_code": first_item.get("hs_code"),
                "productsFileInfo": []
            }

            for item in data:

                fileInfo = {
                    "file_name": item.get("file_name"),
                    "file_path": item.get("file_path"),
                    "file_type": item.get("method"),
                    "hash": item.get("hash"),
                    "confidence": item.get("confidence"),
                    "valid": item.get("valid"),
                    "text": item.get("text"),
                    "text_length": item.get("text_length"),
                    "visual": item.get("visual", {}),
                    "clause": item.get("clause", []),
                    "sub_folder_name": item.get("sub_folder_name"),
                    "product_info": item.get("product_info"),
                    "translated_text": item.get("translated_text")
                }

                result["productsFileInfo"].append(fileInfo)

            return result

        except Exception as e:

            print("Error:", str(e))
            return {}

    @staticmethod
    async def buildResponseOfStandard(data):

        standard = []

        for item in data:

            try:

                text_data = str(
                    item.get("metaText", "")
                )

                # remove null bytes
                text_data = text_data.replace(
                    "\x00",
                    ""
                )

                # utf safe
                text_data = text_data.encode(
                    "utf-8",
                    errors="ignore"
                ).decode("utf-8")

                # skip empty text
                if not text_data.strip():
                    continue

                val = {

                    "standard_id": item.get("std_id"),

                    "std_name": item.get("std_name"),

                    "file_name": item.get("file_name"),

                    "text": text_data,

                    "confidence": item.get("confidence"),

                    "clause": item.get("clause")
                }

                standard.append(val)

            except Exception as e:

                print(
                    "Skipping bad record:",
                    str(e)
                )

                continue

        return standard

    @staticmethod
    async def buildResponseOfTechnicalRegulation(data):

        technical_regulation = []

        for item in data:

            val = {
                "tr_id": item.get("tr_id"),
                "tr_name": item.get("tr_name"),
                "text": item.get("metaText"),
                "file_name": item.get("file_name"),
                "meta_json": item.get("metaJson")
            }

            technical_regulation.append(val)

        return technical_regulation

    @staticmethod
    async def buildResponseOfKsaSaleem(data):
        try:

            if data is None:
                print("data is None")
                return []

            ksa_saleem = []

            for index, item in enumerate(data):

                # skip None
                if item is None:
                    print(f"item is None at index {index}")
                    continue

                # skip empty {}
                if not isinstance(item, dict):
                    print(f"Invalid item type at index {index}")
                    continue

            # skip empty dict
                if len(item.keys()) == 0:
                    print(f"Empty dict at index {index}")
                    continue

                fields = [
                    "ksa_id",
                    "ksa_name",
                    "file_name",
                    "metaText",
                    "confidence",
                    "clause"
                ]

                for field in fields:
                    if item.get(field) is None:
                        print(f"{field} is None in item index {index}")

                val = {
                    "ksa_id": item.get("ksa_id"),
                    "ksa_name": item.get("ksa_name"),
                    "file_name": item.get("file_name", ""),
                    "text": item.get("metaText", ""),
                    "confidence": item.get("confidence", ""),
                    "clause": item.get("clause", {})
                }

                ksa_saleem.append(val)

            print("total docs", len(ksa_saleem))

            return ksa_saleem

        except Exception as e:
            print("ERROR:", str(e))
            return []
    @staticmethod
    async def buildResponseOfSaber(data):

        try:

            if data is None:

                print("data is None")

                return []

            saber = []

            for index, item in enumerate(data):

                try:

                    # =========================
                    # SKIP NONE
                    # =========================
                    if item is None:

                        print(
                            f"item is None at index {index}"
                        )

                        continue

                    # =========================
                    # SKIP EXCEPTION OBJECTS
                    # =========================
                    if isinstance(item, Exception):

                        print(
                            f"Exception object at index {index}:",
                            str(item)
                        )

                        continue

                    # =========================
                    # ENSURE DICT
                    # =========================
                    if not isinstance(item, dict):

                        print(
                            f"Invalid type at index {index}:",
                            type(item)
                        )

                        continue

                    # =========================
                    # SKIP EMPTY OBJECT
                    # =========================
                    if not item:

                        print(
                            f"empty object at index {index}"
                        )

                        continue

                    # =========================
                    # CLEAN TEXT
                    # =========================
                    text_data = str(
                        item.get(
                            "metaText",
                            ""
                        )
                    )

                    text_data = text_data.replace(
                        "\x00",
                        ""
                    )

                    text_data = text_data.encode(
                        "utf-8",
                        errors="ignore"
                    ).decode("utf-8")

                    if not text_data.strip():

                        print(
                            f"empty text at index {index}"
                        )

                        continue

                    # =========================
                    # BUILD OBJECT
                    # =========================
                    val = {

                        "saber_id": item.get(
                            "saber_id"
                        ),

                        "saber_name": item.get(
                            "saber_name"
                        ),

                        "file_name": item.get(
                            "file_name",
                            ""
                        ),

                        "text": text_data,

                        "confidence": item.get(
                            "confidence",
                            ""
                        ),

                        "clause": item.get(
                            "clause",
                            ""
                        )
                    }

                    saber.append(val)

                except Exception as e:

                    print(
                        f"Skipping bad record at index {index}:",
                        str(e)
                    )

                    continue

            print("total docs", len(saber))

            return saber

        except Exception as e:

            print("ERROR:", str(e))

            return []
   
    @staticmethod    
    async def prepare_file_info_data(
            product_id: int,
            files_data: List[Dict]
        ) -> List[Dict]:

            prepared_files = []

            for item in files_data:

                file_info = {

                    # =========================
                    # RELATION
                    # =========================

                    "product_id": product_id,

                    # =========================
                    # FILE INFO
                    # =========================

                    "file_name": item.get("file_name"),

                    "file_path": item.get("file_path"),

                    "file_type": item.get("file_type"),

                    "file_hash": item.get("hash"),

                    # =========================
                    # VALIDATION
                    # =========================

                    "confidence_score": item.get("confidence", 0),

                    "is_valid": item.get("valid", False),

                    # =========================
                    # OCR / TEXT
                    # =========================

            

                    "text": item.get("translated_text"),

                    "text_length": item.get("text_length", 0),

                    # =========================
                    # EXTRACTION DATA
                    # =========================

                    "visual_data": item.get("visual", {}),

                    "clause_data": item.get("clause", []),

                    # =========================
                    # META
                    # =========================

                    "sub_folder_name": item.get("sub_folder_name"),

                    "product_info": item.get("product_info"),
                }

                prepared_files.append(file_info)

            return prepared_files