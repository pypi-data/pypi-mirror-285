""" Classes for handling dataset-related HTTP requests.
"""

from typing import List, Dict
from loguru import logger
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse
from aimmocore.server.schemas.datasets import (
    Dataset,
    DatasetList,
    DatasetFile,
    ThumbnailPageList,
    Thumbnail,
    Embeddings,
    EmbeddingsList,
)
from aimmocore.server.services import datasets as svc


class DatasetExportRouter(HTTPEndpoint):
    """Endpoint for exporting datasets to a file."""

    async def get(self, request: Request):
        """Handles GET requests to export dataset files as a JSON file.

        Args:
            request (Request): The HTTP request object.

        Returns:
            JSONResponse: Error message if dataset_id is not provided or if no data is found to export.
            FileResponse: The generated JSON file.
        """
        dataset_id = request.query_params.get("datasetId", None)
        if not dataset_id:
            return JSONResponse({"message": "dataset_id is required"}, status_code=404)

        file_name = request.query_params.get("fileName", None)
        filter_value = parse_filter_value(request.query_params.get("filterValue", None))

        file_path, file_name = await svc.export_dataset_files_async(dataset_id, file_name, filter_value)
        if not file_path:
            return JSONResponse({"message": "No data to export"}, status_code=404)
        headers = {"Content-Disposition": f"attachment; filename={file_name}"}
        return FileResponse(file_path, headers=headers, filename=file_name, media_type="application/json")


class DatasetRouter(HTTPEndpoint):
    """
    DatasetRouter class handles GET requests for fetching the dataset list.
    It filters datasets by name provided in query parameters and returns
    the results as a JSON response.
    """

    async def get(self, request: Request):
        """
        Handles GET requests to retrieve a list of datasets.
        Filters the datasets by the 'name' query parameter, sorts the results
        by 'created_at' in descending order, and returns the results as a JSON response.

        Args:
            request (Request): Request dataset to list

        Returns:
            JSONResponse: A JSON response containing the filtered and sorted list of datasets.
        """

        name = request.query_params.get("name", "")
        status = request.query_params.get("status", "")
        dataset_list = await svc.get_dataset_list_async(name, status)
        datasets = [Dataset(**dataset) for dataset in dataset_list]
        return JSONResponse(DatasetList(items=datasets).model_dump(by_alias=True))

    async def delete(self, request: Request):
        """
        Handles DELETE requests to delete a dataset by dataset_id.

        Args:
            request (Request): The incoming request object.

        Returns:
            JSONResponse: A JSON response indicating the result of the delete operation.
        """
        # Retrieve the dataset_id from the query parameters.
        dataset_id = request.query_params.get("datasetId")

        if not dataset_id:
            return JSONResponse({"message": "dataset_id is required"})

        logger.debug(f"Delete dataset {dataset_id}")  # Log message indicating the start of deleting a dataset

        try:
            await svc.delete_dataset(dataset_id)
            return JSONResponse({"message": "Deletion of dataset completed"})
        except Exception as e:  # pylint: disable=broad-except
            logger.error(f"Error deleting dataset {dataset_id}: {e}")
            return JSONResponse({"message": "Failed to delete dataset"})


class DatasetFileRouter(HTTPEndpoint):
    """The endpoint for fetching a list of dataset files.

    Args:
        HTTPEndpoint (_type_): _description_
    """

    async def get(self, request: Request):
        dataset_id = request.query_params.get("datasetId", None)
        if not dataset_id:
            return JSONResponse({"message": "datasetId is required"})
        file_id = request.query_params.get("fileId", None)
        if not file_id:
            return JSONResponse({"message": "fileId is required"})

        result = await svc.get_dataset_file_async(dataset_id, file_id)
        if result:
            return JSONResponse(DatasetFile(**result[0]).model_dump(by_alias=True))
        return JSONResponse({"message": "No data found"}, status_code=404)


class DatasetFileListRouter(HTTPEndpoint):
    """The endpoint for fetching a list of dataset files.

    Args:
        HTTPEndpoint (_type_): _description_
    """

    async def get(self, request: Request):
        dataset_id = request.query_params.get("datasetId", None)
        if not dataset_id:
            return JSONResponse({"message": "dataset_id is required"})

        query = {
            "dataset_id": dataset_id,
            "page": int(request.query_params.get("page", 1)),
            "per_page": int(request.query_params.get("perPage", 20)),
            "sort": request.query_params.get("sort", ""),
        }
        filter_value = parse_filter_value(request.query_params.get("filterValue", None))
        items, total_size = await svc.get_dataset_file_list_async(query, filter_value)
        return JSONResponse(
            ThumbnailPageList(
                items=[Thumbnail(**r) for r in items],
                page=query["page"],
                perPage=query["per_page"],
                total=total_size,
            ).model_dump(by_alias=True)
        )


class MetaAggregationRouter(HTTPEndpoint):
    """_summary_

    Args:
        HTTPEndpoint (_type_): _description_
    """

    async def get(self, request: Request):
        dataset_id = request.query_params.get("datasetId", None)
        if not dataset_id:
            return JSONResponse({"message": "dataset_id is required"})

        filterValue = parse_filter_value(request.query_params.get("filterValue", None))
        logger.debug(f"Get meta aggregation for dataset {dataset_id} with filter {filterValue}")
        results = await svc.get_dataset_meta_aggregation(dataset_id, filterValue)
        return JSONResponse(results)


class EmbeddingRouter(HTTPEndpoint):
    """_summary_

    Args:
        HTTPEndpoint (_type_): _description_
    """

    async def get(self, request: Request):
        dataset_id = request.query_params.get("datasetId", None)
        if not dataset_id:
            return JSONResponse({"message": "dataset_id is required"})

        filterValue = parse_filter_value(request.query_params.get("filterValue", None))
        logger.debug(f"Get embedding for dataset {dataset_id} with filter {filterValue}")
        results = await svc.get_dataset_embeddings_async(dataset_id, filterValue)
        items = [Embeddings(**embeddings) for embeddings in results]
        return JSONResponse(EmbeddingsList(items=items).model_dump(by_alias=True))


def parse_filter_value(filter_value) -> Dict[str, List[str]]:
    """
    Parses a filter value string into a dictionary of filters.
    Args:
        filter_value (str): A string containing the filter criteria, formatted as
                            'key:value1,value2;key2:value3,value4'.

    Returns:
        Dict[str, List[str]]: A dictionary where each key is the filter name and each value is a list
                              of strings representing the filter values. If the input string is improperly
                              formatted, it logs an error and returns an empty dictionary.
    """
    filters = {}
    if filter_value:
        try:
            for group in filter_value.split(";"):
                key, value = group.split(":")
                filters[key] = value.split(",")
        except ValueError:
            logger.error(f"Failed to parse :{filter_value}, returning empty filter. Need format: 'metas:rainy,day'")
            filters = {}
    return filters
