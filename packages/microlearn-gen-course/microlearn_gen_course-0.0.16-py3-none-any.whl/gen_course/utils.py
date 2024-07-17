import json
import re


def extract_json_from_text(text):
    """
    Extracts JSON content from a given text.

    Args:
    text (str): Text from which JSON content needs to be extracted.

    Returns:
    dict: Json content extracted from the text.
    """
    json_pattern = re.compile(r'((\[[^\}]{3,})?\{s*[^\}\{]{3,}?:.*\}([^\{]+\])?)', re.DOTALL)
    match = json_pattern.search(text)

    if match:
        json_str = match.group(0)
        try:
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError:
            raise
    else:
        raise
