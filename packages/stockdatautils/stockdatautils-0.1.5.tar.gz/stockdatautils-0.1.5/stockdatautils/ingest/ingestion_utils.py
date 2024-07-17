import requests
import json
import time
from collections import OrderedDict

from datetime import timedelta

from stockdatautils.ingest.utils import get_date_utc, convert_keys_to_snake_case, convert_values


def build_api_url(base_url, params, symbol, api_key):
    """
    Constructs the API URL from the base URL and parameters dictionary.

    Parameters:
    base_url (str): The base URL for the API endpoint.
    params (dict): A dictionary of parameters to be included in the URL.
    symbol (str): The symbol for the stock.
    api_key (str): The API key for authentication.

    Returns:
    str: The complete API URL with parameters.
    """
    params['symbol'] = symbol
    params['apikey'] = api_key
    return base_url + '?' + '&'.join([f"{key}={value}" for key, value in params.items()])


def call_api(base_url, params, symbol, api_key):
    """
    Calls the API with the given parameters and returns the response.

    Parameters:
    base_url (str): The base URL for the API endpoint.
    params (dict): A dictionary of parameters to be included in the URL.
    symbol (str): The symbol for the stock.
    api_key (str): The API key for authentication.

    Returns:
    dict: The JSON response from the API.
    """
    url = build_api_url(base_url, params, symbol, api_key)
    response = requests.get(url, timeout=10)
    time.sleep(0.5)
    return response.json()


def add_utc_timestamp_to_beginning(json_data, days=None):
    """
    Adds a key/value pair to the beginning of a JSON object.

    Parameters:
    json_data (dict): The original JSON data.

    Returns:
    dict: The updated JSON data with the new key/value pair at the beginning.
    """
    if days is not None:
        utc_datetime = get_date_utc() - timedelta(days=days)
    else:
        utc_datetime = get_date_utc()


    # Convert the original dictionary to an OrderedDict
    ordered_data = OrderedDict(json_data)

    # Create a new OrderedDict with the new key/value pair
    new_ordered_data = OrderedDict({"src_date": utc_datetime})

    # Update the new OrderedDict with the original data
    new_ordered_data.update(ordered_data)

    # Convert back to a regular dictionary (if necessary)
    return dict(new_ordered_data)


def process_json(json_data):
    """
    Process a JSON object by adding a UTC timestamp, converting all keys to snake_case, and converting values to their inferred types.

    Parameters:
    json_data (dict): The original JSON data.

    Returns:
    dict: The processed JSON data with a UTC timestamp, snake_case keys, and inferred value types.
    """
    # Add UTC timestamp to the beginning
    json_data_with_timestamp = add_utc_timestamp_to_beginning(json_data)

    # Convert all keys to snake_case
    json_data_snake_case = convert_keys_to_snake_case(json_data_with_timestamp)

    # Convert all values to their inferred types
    cleaned_json_data = convert_values(json_data_snake_case)

    return cleaned_json_data


def custom_upsert(collection, symbol, date, query, document):
    """Custom upsert function to insert a document if it doesn't exist."""
    if not collection.find_one(query):
        collection.insert_one(document)
    else:
        print(
            f"Document for {symbol} on {date} already exists in '{collection}' collection. Skipping insert.")
