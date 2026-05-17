import pandas as pd


def read_excel_file(file_path: str):

    if file_path.lower().endswith(".csv"):

        return pd.read_csv(
            file_path,
            dtype=str,
            low_memory=False
        )

    return pd.read_excel(
        file_path,
        dtype=str
    )


def extract_excel(file_path: str):

    try:

        # =========================
        # READ FILE
        # =========================
        df = read_excel_file(file_path)

        # =========================
        # CLEAN NULL VALUES
        # =========================
        df = df.fillna("")

        # =========================
        # CONVERT DATAFRAME TO TEXT
        # =========================
        text = "\n".join(
            df.astype(str)
            .agg(" ".join, axis=1)
            .tolist()
        )

        # =========================
        # STRUCTURED OUTPUT
        # =========================
        structured = {
            "columns": list(df.columns),
            "rows": len(df)
        }

        return (
            text,
            structured,
            "excel",
            1.0
        )

    except Exception as error:

        print(f"Excel extraction error: {error}")

        return "", {}, "failed", 0.0


def extract_excel1(file_path: str):

    try:

        print(
            f"Extracting HS code from Excel file: {file_path}"
        )

        # =========================
        # READ FILE
        # =========================
        df = read_excel_file(file_path)

        # =========================
        # CLEAN NULL VALUES
        # =========================
        df = df.fillna("")

        return df

    except Exception as error:

        print(f"Excel extraction error: {error}")

        return pd.DataFrame()