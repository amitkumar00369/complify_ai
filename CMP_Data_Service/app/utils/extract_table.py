import pdfplumber
import pandas as pd


def extract_tables(pdf_path):

    all_rows = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                if not table:
                    continue

                for row in table:

                    if row:
                        all_rows.append(row)

    return all_rows