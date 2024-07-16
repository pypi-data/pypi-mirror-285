import aiofiles
import json
import hashlib
import time
import re
import unicodedata


def now():
    """현재 시간을 밀리초 단위로 반환합니다."""
    return int(time.time() * 1000)


def hash_filename(filename):
    md5_hash = hashlib.md5()
    md5_hash.update(filename.encode("utf-8"))
    return md5_hash.hexdigest()


async def write_to_file(file_path: str, datas: list):
    """
    Writes request data to a file asynchronously.

    Args:
        file_path (str): The path to the file to write the request data to
        request_datas (list): The list of request data to be written to the file.
    """
    async with aiofiles.open(file_path, "w", encoding="utf-8") as file:
        for d in datas:
            await file.write(json.dumps(d, ensure_ascii=False) + "\n")


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
