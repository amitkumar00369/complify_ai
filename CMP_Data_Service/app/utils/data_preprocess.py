
from fastapi import HTTPException
import pandas as pd
import io
import json
from fastapi.responses import JSONResponse
from app.utils.enum import bussinesType
import fitz
from app.services.clause_splitter import split_clauses
from app.services.clause_parser import parse_clause
class dataExtractionProcess:

    @staticmethod
    def prepare_json_data(data):
        data = json.loads(data.decode("utf-8"))
        df = pd.DataFrame(data)
        return df
    
    @staticmethod
    def prepare_csv_data(data):
        df = pd.read_csv(io.StringIO(data.decode("utf-8")))
        return df
    
    @staticmethod
    def prepare_excel_data(data):
        df = pd.read_excel(io.BytesIO(data), engine="openpyxl")
        return df
    
    @staticmethod
    def prepare_excel_old_version_data(data):
        df = pd.read_excel(io.BytesIO(data), engine="xlrd")
        return df
    @staticmethod
    def prepare_txt_data(data):
        text_data = data.decode("utf-8").strip()

        try:
            json_data = json.loads(text_data)  # try JSON parse
            df = pd.DataFrame(json_data)
            return df
        except json.JSONDecodeError:
            return JSONResponse(content={"status":400, "message": "TXT file is not valid JSON format"},status_code=400)
    @staticmethod
    def prepare_pdf_data(data):
        try:
              # STEP 1: Extract full text
            doc = fitz.open(data)
            text = ""

            for page in doc:
                text += page.get_text()
                
            print("hii",text)

            # STEP 2: Split into clauses (AFTER full text)
            raw_clauses = split_clauses(text)
            print("dfghgh",raw_clauses)

            # STEP 3: Parse clauses
            parsed = []

            for c in raw_clauses:
                print(c)
                clause = parse_clause(c)

                if clause.get("field"):  # only useful clauses
                    parsed.append({
                        "original_text": c,
                        "parsed": clause
                    })
            print("parsed",parsed)

            return parsed

            # return text
        except json.JSONDecodeError:
            return JSONResponse(content={"status":400, "message": "TXT file is not valid JSON format"},status_code=400)
  
    
DataExtractionProcess = dataExtractionProcess()