import re
import json

from datetime import datetime
from pytz import timezone


def get_api_key(file_path):
    """
    Extracts the API key from a given JSON file.

    Args:
        file_path (str): The path to the JSON file containing the API key.

    Returns:
        str: The API key extracted from the JSON file. If the key is not found, returns None.

    Raises:
        FileNotFoundError: If the file at the given path does not exist.
        json.JSONDecodeError: If the file is not a valid JSON.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            api_key = data.get("api_key")
            return api_key
    except FileNotFoundError as fnf_error:
        print(f"Error: {fnf_error}")
        raise
    except json.JSONDecodeError as json_error:
        print(f"Error: {json_error}")
        raise


def get_utc_date(d):
    # Convert UTC time to GMT timezone
    gmt = timezone("GMT")

    utc_datetime = gmt.localize(d).replace(
        hour=0, minute=0, second=0, microsecond=0)

    return utc_datetime


def to_snake_case(name):
    """
    Convert a given string to snake_case.

    This function replaces dots with underscores, replaces multiple spaces with a single underscore,
    converts CamelCase to snake_case, and ensures no multiple underscores are present.

    Parameters:
    name (str): The string to be converted to snake_case.

    Returns:
    str: The converted snake_case string.
    """
    # remove dots
    name = name.replace('.', '')
    # Replace multiple spaces with a single underscore
    name = re.sub(r'\s+', '_', name)
    # Convert CamelCase to snake_case
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # Ensure no multiple underscores
    name = re.sub(r'_+', '_', s2)
    return name.lower()


def convert_keys_to_snake_case(data):
    """
    Recursively convert all keys in a dictionary or list of dictionaries to snake_case.

    This function will process each key in the input data structure and convert it to snake_case
    using the to_snake_case function. It handles nested dictionaries and lists of dictionaries.

    Parameters:
    data (dict or list): The data structure (dictionary or list of dictionaries) whose keys need to be converted to snake_case.

    Returns:
    dict or list: The data structure with all keys converted to snake_case.
    """
    if isinstance(data, dict):
        return {to_snake_case(key): convert_keys_to_snake_case(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_snake_case(item) for item in data]
    else:
        return data


def infer_type(value):
    """
    Infers and converts the value to the appropriate type.

    Parameters:
    value (str): The string value to be converted.

    Returns:
    int, float, or str: The converted value in its inferred type.
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def convert_values(data):
    """
    Recursively converts all string values in a dictionary or list to their inferred types.

    Parameters:
    data (dict or list): The data structure containing the values to be converted.

    Returns:
    dict or list: The data structure with all values converted to their inferred types.
    """
    if isinstance(data, dict):
        return {key: convert_values(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_values(item) for item in data]
    elif isinstance(data, str):
        return infer_type(data)
    else:
        return data
