""" This module contains utility functions used by the core module. """

import json
import hashlib
import time
import re
from functools import wraps
import unicodedata
import requests
import aiofiles
from bson import ObjectId
from bson.errors import InvalidId
from loguru import logger


def now():
    """Returns the current timestamp in milliseconds."""
    return int(time.time() * 1000)


def hash_filename(filename: str) -> str:
    """Generates an MD5 hash of the given filename.

    Args:
        filename (str): The filename to hash.

    Returns:
        str: The MD5 hash of the filename.
    """

    md5_hash = hashlib.md5()
    md5_hash.update(filename.encode("utf-8"))
    return md5_hash.hexdigest()


async def write_to_file(file_path: str, datas: list) -> bool:
    """Writes request data to a file asynchronously.

    Args:
        file_path (str): The path to the file to write the request data to.
        datas (list): The list of request data to be written to the file.

    Returns:
        bool: True if writing to the file is successful, False otherwise.
    """
    try:
        async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
            for d in datas:
                await file.write(json.dumps(d, ensure_ascii=False) + "\n")
        return True
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Error writing to file: {e}")
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitizes a string to make it a valid filename.

    Args:
        filename (str): The original filename string.

    Returns:
        str: The sanitized filename string.
    """
    # Normalize the unicode string
    filename = unicodedata.normalize("NFKD", filename)

    # Replace spaces with underscores
    filename = filename.replace(" ", "_")

    # Remove invalid characters
    filename = re.sub(r"[^\w\-_\.]", "", filename)

    return filename


def is_supported_ext(file_name: str, supported_extensions: list) -> bool:
    """Check if the file has a supported extension.

    Args:
        file_name (str): file name
        supported_extensions (list): list of supported extensions

    Returns:
        bool: True if the file has a supported extension, False otherwise.
    """
    return any(file_name.lower().endswith(ext) for ext in supported_extensions)


def validate_dataset_id(func):
    """
    Decorator to validate if the 'dataset_id' argument is a valid MongoDB ObjectId.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Find the dataset_id argument
        if "dataset_id" in kwargs:
            value = kwargs["dataset_id"]
        else:
            arg_names = func.__code__.co_varnames
            if "dataset_id" in arg_names:
                index = arg_names.index("dataset_id")
                if index < len(args):
                    value = args[index]
                else:
                    raise ValueError("Missing required parameter 'dataset_id'")
            else:
                raise ValueError("Parameter 'dataset_id' not found")

        # Validate the ObjectId
        if not isinstance(value, str):
            raise ValueError("Parameter 'dataset_id' must be a string representing an ObjectId.")
        try:
            ObjectId(value)
        except (InvalidId, TypeError):
            raise ValueError("Invalid ObjectId string for parameter 'dataset_id'")  # pylint: disable=raise-missing-from

        return func(*args, **kwargs)

    return wrapper


def make_get_request(url: str, headers: dict, timeout: int = 30) -> dict:
    """Make a GET request to the given URL.

    Args:
        url (str): The URL to make the GET request to.
        headers (dict): The headers to include in the request.
        timeout (int, optional): The request timeout in seconds. Defaults to 30.

    Returns:
        dict: _description_
    """
    response = requests.get(url, headers=headers, timeout=timeout)
    if response.status_code == 200:
        return response.json()
    logger.info(f"The server's doing a quick dance. Please try again! [{response.status_code}]")
    return {"status": "Error"}
