from loguru import logger
from PIL import Image
import aiohttp
from io import BytesIO
from pymongo import UpdateOne
from aimmocore import config as conf


def create_thumbnail(image_data, image_id, size=(274, 274)):
    try:
        with Image.open(BytesIO(image_data)) as img:
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.thumbnail((max(size), max(size)))
            thumbnail_path = f"{conf.THUMBNAIL_DIR}/{image_id}.jpg"
            img.save(thumbnail_path, "JPEG")
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Error creating thumbnail for image ID {image_id}: {e}")


async def download_image(session, image_url):
    """이미지 URL에서 이미지를 다운로드합니다."""
    try:
        async with session.get(image_url) as response:
            response.raise_for_status()
            return await response.read()
    except Exception as e:  # pylint: disable=broad-except
        logger.error(f"Error downloading image {image_url}: {e}")
        return None


async def process_image(document, session):
    """MongoDB 문서에서 이미지 URL을 가져와 썸네일을 생성합니다."""
    image_id = document.get("id")
    image_url = document.get("image_url")
    if image_id and image_url:
        image_data = await download_image(session, image_url)
        if image_data:
            create_thumbnail(image_data, image_id)
            return image_id
    return None


async def generate_thumbnail(db):
    """
    Generate thumbnails for images in the database and update their status.

    This function fetches documents from the database where the thumbnail status is neither "Y" (completed)
    nor "P" (in progress). It then processes each image to generate a thumbnail and updates the status
    accordingly in the database.

    Args:
        db: The database connection object.

    Returns:
        None
    """
    logger.info("Generating thumbnails for images...")
    async with aiohttp.ClientSession() as session:
        collection = db.engine.raw_files
        documents = await collection.find({"thumbnail": {"$nin": ["Y", "P"]}}, {"_id": 0}).to_list(None)

        image_ids_in_progress = [document.get("id") for document in documents]
        await collection.update_many({"id": {"$in": image_ids_in_progress}}, {"$set": {"thumbnail": "P"}})
        completed_image_ids = []
        for document in documents:
            completed_image_ids.append(await process_image(document, session))

        # Create a list of update requests to set the thumbnail status to "Y" (completed)
        # for successfully processed images.
        requests = [
            UpdateOne({"id": image_id}, {"$set": {"thumbnail": "Y"}})
            for image_id in completed_image_ids
            if image_id is not None
        ]

        # Perform a bulk write operation to update the thumbnail status in MongoDB.
        if requests:
            result = await collection.bulk_write(requests)
            logger.debug(f"Bulk write result: {result.bulk_api_result}")
