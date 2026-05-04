import hashlib
import os
import re


def sha256(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def normalize(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def validate(text):
    if len(text) < 30:
        return False
    return True


def valid_file(path):
    return os.path.exists(path) and os.path.getsize(path) > 0

# def find_hs_code(text):
#     #  simple regex for HS code (6-10 digits)
#      # example  843850000002
#     match = re.search(r'\b\d{6,10}\b', text)
#     return match.group(0) if match else None