import os
from pymongo import UpdateOne
from loguru import logger
from aimmocore.core import utils as ut
from urllib.parse import urlparse, unquote


def extract_filename_from_image_url(url):
    """
    Extracts the filename from a given image URL.

    This function parses the given URL to extract the path component, unquotes it (to convert percent-encoded characters back to their normal representation), and then returns the filename part of the path.

    Args:
        url (str): The URL from which to extract the filename.

    Returns:
        str: The extracted filename from the URL.
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    filename = unquote(path)
    return filename


async def insert_raw_files(db, files_info: list):
    """Insert raw files information into the database. md5 hash is used as the unique identifier.

    Args:
        db (_type_): The database connection.
        files_info (list): A list of dictionaries containing file information.
    """
    try:
        operations = [
            UpdateOne(
                {"id": item["id"]},
                {
                    "$setOnInsert": {
                        "id": item["id"],
                        "image_url": item["image_url"],
                        "file_name": extract_filename_from_image_url(item["image_url"]),
                        "file_size": item["file_size"],
                        "thumbnail_url": f"{item['id']}.jpg",
                    }
                },
                upsert=True,
            )
            for item in files_info
        ]

        if operations:
            await db.engine.raw_files.bulk_write(operations)

    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Something wrong!: {e}")


async def insert_raw_dataset(db, name: str, dataset_id: str, raw_data_list: list):
    """Insert raw dataset information into the database.

    Args:
        db (_type_): The database connection.
        name (str): The name of the dataset.
        dataset_id (str): The ID of the dataset.
        raw_data_list (list): A list of dictionaries containing raw data information.
    """
    try:
        # Prepare raw dataset documents
        created_at = ut.now()
        raw_datasets = [
            {"dataset_id": dataset_id, "image_id": item["id"], "created_at": created_at} for item in raw_data_list
        ]

        # Insert raw datasets
        if raw_datasets:
            await db.engine.datasets.insert_many(raw_datasets)
            logger.debug(f"Inserted {len(raw_datasets)} raw datasets.")

        # Insert dataset info if raw_data_list is not empty
        if raw_data_list:
            await db.engine.dataset_info.update_one(
                {"dataset_id": dataset_id},
                {
                    "$set": {
                        "dataset_name": name,
                        "dataset_id": dataset_id,
                        "model_types": raw_data_list[0].get("model_type", []),
                        "status": "Preparing",
                        "applied_metas": [],
                        "embedding_model": "Not Applied",
                        "file_count": len(raw_data_list),
                        "created_at": created_at,
                    }
                },
                upsert=True,
            )
            logger.debug(f"Inserted/Updated dataset info for dataset_id: {dataset_id}.")

    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Something went wrong!: {e}")


async def update_dataset_info(db, dataset_id: str, status: str, meta_list: list, count: int = 0):
    """_summary_

    Args:
        db (_type_): _description_
        dataset_id (str): _description_
        status (str): _description_
        meta_list (list): _description_
        count (int, optional): processed curated image count
    """
    updated_time = ut.now()

    # extract meta information
    meta_info = [meta["name"] for meta in meta_list]

    try:
        await db.engine.dataset_info.update_one(
            {"dataset_id": dataset_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": updated_time,
                    "applied_metas": meta_info,
                    "embedding_model": "Applied",
                    "curation_count": count,
                }
            },
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Something went wrong!: {e}")


async def update_dataset_info_status(db, dataset_id: str, status: str):
    """_summary_

    Args:
        db (_type_): _description_
        dataset_id (str): _description_
        status (str): _description_
    """
    updated_time = ut.now()

    try:
        await db.engine.dataset_info.update_one(
            {"dataset_id": dataset_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": updated_time,
                }
            },
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Something went wrong!: {e}")


async def update_curation_results(db, dataset_id: str, results: dict):
    """Updates curation results in the datasets collection.

    Args:
        db (_type_): Motor client
        dataset_id (str): The ID of the dataset
        curation_results (list): The list of curation results
    """
    updated_time = ut.now()
    try:
        operations = [
            UpdateOne(
                {"dataset_id": dataset_id, "image_id": result["file_id"]},
                {
                    "$set": {
                        "embeddings": result["curations"],
                        "metas": result["metas"],
                        "updated_at": updated_time,
                    }
                },
            )
            for result in results["emd_results"]
        ]

        if operations:
            await db.engine.datasets.bulk_write(operations, ordered=False)
            logger.debug(f"Updated {len(operations)} curation results for dataset_id: {dataset_id}.")
            # i think not good code.
            return results["emd_results"][0]["metas"]
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Something went wrong!: {e}")


async def update_dataset_curation_status(db, status_info: dict):
    """_summary_

    Args:
        db (_type_): _description_
        status (dict): _description_
    """
    dataset_id = status_info["dataset_id"]
    new_status = status_info["status"]

    collection = db.engine.dataset_info
    existing_status = await collection.find_one({"dataset_id": dataset_id})
    current_time = ut.now()
    if existing_status:
        await collection.update_one(
            {
                "dataset_id": dataset_id,
            },
            {"$set": {"status": new_status, "updated_at": current_time}},
        )


def delete_file(file_path):
    try:
        os.remove(file_path)
    except FileNotFoundError:
        logger.error(f"File {file_path} not found.")
    except PermissionError:
        logger.error(f"Permission denied: unable to delete {file_path}.")
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"An error occurred while deleting the file {file_path}: {e}")
