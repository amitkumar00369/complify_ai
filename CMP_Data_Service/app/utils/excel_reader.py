import pandas as pd
from datetime import date
from io import BytesIO
from fastapi import UploadFile


def clean_value(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value.lower() == "nan":
        return None

    return value


def clean_hs_code(value):
    if pd.isna(value):
        return None

    hs_code = str(value).strip()

    if hs_code.endswith(".0"):
        hs_code = hs_code.replace(".0", "")

    return hs_code.replace(" ", "")


def parse_date(value):
    if pd.isna(value):
        return None

    if isinstance(value, date):
        return value

    try:
        return pd.to_datetime(value).date()
    except Exception:
        return None


def split_hs_code(hs_code: str):
    return {
        "full_hs_code": hs_code,
        "chapter_code": hs_code[:2],
        "heading_code": hs_code[:4],
        "subheading_code": hs_code[:6],
    }


async def read_hs_excel_from_upload(file: UploadFile):
    content = await file.read()
    excel_file = BytesIO(content)

    df = pd.read_excel(excel_file, sheet_name="Grid")
    print("coluns",df.columns)
    records = []

    for index, row in df.iterrows():
        #print("hscode",row.get("رمز النظام المنسق \n Harmonized Code"))
        hs_code = clean_hs_code(row.get("رمز النظام المنسق \n Harmonized Code"))

        if not hs_code or len(hs_code) < 6:
            continue

        records.append({
            **split_hs_code(hs_code),
            "item_name_ar": clean_value(row.get("الصنف باللغة العربية \n Item Arabic Name")),
            "item_name_en": clean_value(row.get("الصنف باللغة الانجليزية \n Item English Name")),
            "duty_rate_ar": clean_value(row.get("فئة الرسم باللغة العربية \n Arabic Duty Rate")),
            "duty_rate_en": clean_value(row.get("فئة الرسم باللغة الانجليزية \n English Duty Rate")),
            "procedure_codes": clean_value(row.get("الاجراءات '\n Procedures")),
            "effective_date": parse_date(row.get("التاريخ \n Date")),
            "source_sheet": "Grid",
            "source_row": index + 2,
        })

     
    # print("Record",records)

    return records

async def read_hs_excel_from_path(
    file_path: str
):

    # ==============================================
    # READ EXCEL DIRECTLY FROM FILE PATH
    # ==============================================
    df = pd.read_excel(
        file_path,
        sheet_name="Grid"
    )

    print(
        "columns:",
        df.columns
    )

    records = []

    for index, row in df.iterrows():

        hs_code = clean_hs_code(
            row.get(
                "رمز النظام المنسق \n Harmonized Code"
            )
        )

        if (
            not hs_code
            or
            len(hs_code) < 6
        ):
            continue

        records.append({

            **split_hs_code(hs_code),

            "item_name_ar": clean_value(
                row.get(
                    "الصنف باللغة العربية \n Item Arabic Name"
                )
            ),

            "item_name_en": clean_value(
                row.get(
                    "الصنف باللغة الانجليزية \n Item English Name"
                )
            ),

            "duty_rate_ar": clean_value(
                row.get(
                    "فئة الرسم باللغة العربية \n Arabic Duty Rate"
                )
            ),

            "duty_rate_en": clean_value(
                row.get(
                    "فئة الرسم باللغة الانجليزية \n English Duty Rate"
                )
            ),

            "procedure_codes": clean_value(
                row.get(
                    "الاجراءات '\n Procedures"
                )
            ),

            "effective_date": parse_date(
                row.get(
                    "التاريخ \n Date"
                )
            ),

            "source_sheet": "Grid",

            "source_row": index + 2,
        })

    return records