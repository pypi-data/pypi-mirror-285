import re

def extract(input_text: str) -> str:
    """
    Extracts JSON content from a given input text.

    Args:
        input_text (str): The input text containing JSON content.

    Returns:
        str: The extracted JSON content, or None if no JSON content is found.
    """
    pattern = r"```json(.*?)```"

    match = re.search(pattern, input_text, re.DOTALL)
    
    if (match):
        return match.group(1).strip()
    else:
        raise("No JSON content found in the input text.")

def save_json_to_file(json_content: str, file_path: str) -> None:
    """
    Saves the given JSON content to a file.

    Args:
        json_content (str): The JSON content to save.
        file_path (str): The path to the file to save the JSON content to.
    """
    try:
        with open(file_path, "x") as file:
            file.write(json_content)
    except Exception as e:
        print(f"Error saving the content as json: {e}")