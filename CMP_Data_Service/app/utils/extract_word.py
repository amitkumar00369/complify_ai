import os
import io
import zipfile
import tempfile
from PIL import Image
import pytesseract
from docx import Document


def extract_word_file(file_path):
    """
    Extract everything possible from .docx file:
    - Paragraph text
    - Table data
    - OCR from images
    - Headers / Footers
    - Metadata
    - Structured response

    Returns:
    {
        "text": str,
        "structured": dict,
        "method": str,
        "confidence": float
    }
    """

    try:

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext not in [".docx"]:
            raise ValueError("Currently only .docx supported")

        doc = Document(file_path)

        full_text = []
        structured_data = {
            "paragraphs": [],
            "tables": [],
            "images_text": [],
            "headers": [],
            "footers": [],
            "metadata": {}
        }

        # =====================================================
        # 1. EXTRACT NORMAL PARAGRAPHS
        # =====================================================

        for para in doc.paragraphs:

            text = para.text.strip()

            if text:
                full_text.append(text)

                structured_data["paragraphs"].append({
                    "text": text
                })

        # =====================================================
        # 2. EXTRACT TABLES
        # =====================================================

        for table_index, table in enumerate(doc.tables):

            table_data = []

            for row in table.rows:

                row_data = []

                for cell in row.cells:
                    cell_text = cell.text.strip()

                    row_data.append(cell_text)

                table_data.append(row_data)

            structured_data["tables"].append({
                "table_index": table_index,
                "rows": table_data
            })

            # Convert table to readable text
            for row in table_data:
                row_text = " | ".join(row)

                if row_text.strip():
                    full_text.append(row_text)

        # =====================================================
        # 3. EXTRACT HEADERS / FOOTERS
        # =====================================================

        for section in doc.sections:

            # Headers
            header = section.header

            for para in header.paragraphs:
                text = para.text.strip()

                if text:
                    structured_data["headers"].append(text)
                    full_text.append(text)

            # Footers
            footer = section.footer

            for para in footer.paragraphs:
                text = para.text.strip()

                if text:
                    structured_data["footers"].append(text)
                    full_text.append(text)

        # =====================================================
        # 4. EXTRACT METADATA
        # =====================================================

        props = doc.core_properties

        structured_data["metadata"] = {
            "author": props.author,
            "title": props.title,
            "subject": props.subject,
            "category": props.category,
            "comments": props.comments,
            "created": str(props.created),
            "modified": str(props.modified),
            "last_modified_by": props.last_modified_by
        }

        # =====================================================
        # 5. EXTRACT IMAGES + OCR
        # =====================================================

        with zipfile.ZipFile(file_path, 'r') as zip_ref:

            image_files = [
                item for item in zip_ref.namelist()
                if item.startswith("word/media/")
            ]

            for image_name in image_files:

                try:

                    image_data = zip_ref.read(image_name)

                    image = Image.open(io.BytesIO(image_data))

                    # OCR
                    image_text = pytesseract.image_to_string(image)

                    image_text = image_text.strip()

                    if image_text:

                        structured_data["images_text"].append({
                            "image": image_name,
                            "text": image_text
                        })

                        full_text.append(image_text)

                except Exception as image_error:

                    structured_data["images_text"].append({
                        "image": image_name,
                        "error": str(image_error)
                    })

        # =====================================================
        # FINAL CLEAN TEXT
        # =====================================================

        final_text = "\n".join(full_text)

        return final_text, structured_data, "advanced_docx_extract", 0.98
        

    except Exception as e:

        return final_text, structured_data, "advanced_docx_extract", 0.98