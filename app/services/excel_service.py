import pandas as pd


def extract_excel(file_path):
    try:
        # =========================
        # READ FILE (SAFE)
        # =========================
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, dtype=str, low_memory=False)
        else:
            df = pd.read_excel(file_path, dtype=str)

        # =========================
        # FILL NA (avoid errors)
        # =========================
        df = df.fillna("")

        # =========================
        # TEXT CONVERSION (FAST)
        # =========================
        # 🔥 faster than apply(lambda...)
        text = "\n".join(
            df.astype(str).agg(" ".join, axis=1).tolist()
        )

        # =========================
        # STRUCTURED OUTPUT
        # =========================
        structured = {
            "columns": list(df.columns),
            "rows": len(df)
        }

        return text, structured, "excel", 1.0

    except Exception as e:
        print("Excel error:", e)
        return "", {}, "failed", 0.0
    
    
    
    
def extract_excel1(file_path):
    try:
        print(f"Extracting HS code from Excel file: {file_path}")
        # =========================
        # READ FILE (SAFE)
        # =========================
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path, dtype=str, low_memory=False)
        else:
            df = pd.read_excel(file_path, dtype=str)

        # =========================
        # FILL NA (avoid errors)
        # =========================
        df = df.fillna("")

        # =========================
        # TEXT CONVERSION (FAST)
        # =========================
        # 🔥 faster than apply(lambda...)
     
        return df

    except Exception as e:
        print("Excel error:", e)
        return "", {}, "failed", 0.0