import re

def split_clauses(text):
    # normalize spaces
    text = re.sub(r'\s+', ' ', text)

    # split on period followed by space or newline
    sentences = re.split(r'\.\s+|\n+', text)

    return [s.strip() for s in sentences if len(s.strip()) > 15]