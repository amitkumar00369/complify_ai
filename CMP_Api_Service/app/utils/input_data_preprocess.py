import re
from .data_preprocess import DataExtractionProcess
UPLOAD_DIR = "upload"
def prepare_pdf_data(file,contents):
    
    file_path = f"{UPLOAD_DIR}/{file.filename}"

    # save file
    with open(file_path, "wb") as f:
            f.write(contents)
    text = DataExtractionProcess.prepare_pdf_data(file_path)
    return text
    
    
        
class inputDataProcess:
    
    @staticmethod
    def parse_text_input(text):
        print("teststts",text)
        product = {}
        documents = []

        # voltage
        voltage = re.search(r'(\d+)\s*V', text)
        if voltage:
            product["voltage"] = int(voltage.group(1))

        # frequency
        freq = re.search(r'(\d+)\s*Hz', text)
        if freq:
            product["frequency"] = int(freq.group(1))

        # document detection
        if "test report" in text.lower():
            documents.append("test_report")

        product["market"] = "KSA"

        return {
            "product": product,
            "documents": documents
        }
    @staticmethod
    def pdf_to_input(file_path):
        parsed = prepare_pdf_data(file_path)

        product = {}
        documents = []

        for item in parsed:
            field = item["parsed"]["field"]
            action = item["parsed"]["action"]

            if field == "voltage":
                product["voltage"] = action.get("max")

            elif field == "frequency":
                product["frequency"] = action.get("value")

            elif field == "test_report":
                documents.append("test_report")

        product["market"] = "KSA"

        return {
            "product": product,
            "documents": documents
        }
        
InputDataProcess=inputDataProcess()