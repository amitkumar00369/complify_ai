import json
import os


def load_json_file(path: str):

    if not os.path.exists(path):
        return []

    try:

        with open(path, "r", encoding="utf-8") as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except Exception as error:

        print(f"JSON load error: {error}")

        return []
    
    
def save_json_file(path: str, data):

    with open(path, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )