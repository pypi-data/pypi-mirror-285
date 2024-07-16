import json
import os

default_content = """{
    "OPEN_AI_API_KEY": "<YOUR OPEN_AI API KEY>",
    "OPEN_ROUTER_API_KEY": "<YOUR OPEN_ROUTER API KEY>",
    "DEEPL_API_KEY": "<YOUR DEEPL API KEY>",
    "GOOGLE_API_KEY": "<YOUR GOOGLE API KEY>",
    "GEMINI_API_KEY": "<YOUR GEMINI API KEY>"
}
"""


def get_key(key_name):
    file_name = "keys.json"
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            keys = json.load(f)
            if key_name in keys:
                return keys[key_name]
            else:
                raise KeyError(f"Key {key_name} not found in keys.json")
    else:
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(default_content)
        raise FileNotFoundError(
            "keys.json in working directory not found. It was created with the default content. Please fill in the keys and try again.")
