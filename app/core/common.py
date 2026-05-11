import hashlib
import os
import re


# =========================================================
# SHA256 HASH
# =========================================================

def sha256(file_path: str) -> str:

    sha = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(8192),
            b""
        ):
            sha.update(chunk)

    return sha.hexdigest()


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize(text: str) -> str:

    if not text:
        return ""

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# VALIDATE TEXT
# =========================================================

def validate(text: str) -> bool:

    return len(text) >= 30


# =========================================================
# VALIDATE FILE
# =========================================================

def valid_file(path: str) -> bool:

    return (
        os.path.exists(path)
        and os.path.isfile(path)
        and os.path.getsize(path) > 0
    )