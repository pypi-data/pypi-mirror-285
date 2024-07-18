"""Datasets service module."""

import json
import asyncio
from typing import List, Dict, Any
from loguru import logger
from aimmocore import config as conf
from aimmocore.core.database import MongoDB
from aimmocore.core.utils import sanitize_filename
from aimmocore.server.schemas.datasets import ProcessStatus

db = MongoDB()


META_TYPE = {
    "weather": ["clear", "cloudy", "rainy"],
    "road_feature": ["city", "highway"],
    "location": ["inside", "outside"],
    "time": ["night", "day", "sunrise/sunset"],
}


def get_dataset_embeddings(dataset_id: str) -> List[Dict]:
    """Retrieve dataset embeddings by dataset_id.

    Args:
        dataset_id (str): dataset id

    Returns:
        List[Dict]: List of dataset embeddings
    """
    return asyncio.get_event_loop().run_until_complete(get_dataset_embeddings_async(dataset_id, {}))


async def get_dataset_embeddings_async(dataset_id: str, filter_value: dict):

    match_query = await build_match_query_with_filter(dataset_id, filter_value)
    match_query["$match"]["updated_at"] = {"$exists": True}
    pipeline = [
        match_query,
        {
            "$lookup": {
                "from": "raw_files",  # Specify the collection to join with
                "localField": "image_id",  # The field from the datasets collection
                "foreignField": "id",  # The field from the raw_files collection
                "as": "raw_files_docs",  # The name of the array field to add to the documents
            }
        },
        {"$unwind": "$raw_files_docs"},  # Deconstruct the array field from the lookup stage
        {
            "$project": {
                "_id": 0,
                "file_id": "$raw_files_docs.id",
                "thumbnail_url": "$raw_files_docs.thumbnail_url",
                "image_url": "$raw_files_docs.image_url",
                "created_at": 1,
                "embedding": {
                    "$arrayElemAt": [
                        {
                            "$filter": {
                                "input": "$embeddings",
                                "as": "item",
                                "cond": {"$eq": ["$$item.name", "embedding"]},
                            }
                        },
                        0,
                    ]
                },
                "curated_mask": {
                    "$arrayElemAt": [
                        {
                            "$filter": {
                                "input": "$embeddings",
                                "as": "item",
                                "cond": {"$eq": ["$$item.name", "curated_mask"]},
                            }
                        },
                        0,
                    ]
                },
                "anomaly_score": {
                    "$arrayElemAt": [
                        {
                            "$filter": {
                                "input": "$embeddings",
                                "as": "item",
                                "cond": {"$eq": ["$$item.name", "anomaly_score"]},
                            }
                        },
                        0,
                    ]
                },
            }
        },
        {
            "$project": {
                "file_id": 1,
                "thumbnail_url": 1,
                "image_url": 1,
                "embeddings": "$embedding.value",
                "curated_mask": "$curated_mask.value",
                "anomaly_score": {"$toDouble": "$anomaly_score.value"},
            }
        },
    ]
    db.connect()
    result = await db.engine.datasets.aggregate(pipeline).to_list(None)
    return result


def validate_status(status: str) -> bool:
    """Validates the status against the ProcessStatus enum.

    Args:
        status (str): The status to validate.

    Returns:
        bool: True if the status is valid, False otherwise.
    """
    try:
        ProcessStatus(status)
        return True
    except ValueError:
        all_status_values = [status.value for status in ProcessStatus]
        logger.error(f"Invalid status '{status}'. Valid statuses are: {all_status_values}")
        return False


def get_dataset_list(name: str = "", status: str = "") -> List[Dict]:
    """from get_dataset_list_async

    Args:
        name (str, optional): _description_. Defaults to "".
        status (str, optional): _description_. Defaults to "".

    Returns:
        List[Dict]: _description_
    """
    return asyncio.get_event_loop().run_until_complete(get_dataset_list_async(name, status))


async def get_dataset_list_async(name: str = "", status: str = "") -> List[Dict]:
    """Get a list of datasets filtered by dataset_name and sorted by created_at in descending order.

    Args:
        name_filter (str, optional): Partial name to filter datasets by. Defaults to "".

    Returns:
        List[Dict]: List of datasets
    """
    db.connect()
    filter_condition = {}
    if name:
        filter_condition["dataset_name"] = {"$regex": name, "$options": "i"}
    if status:
        if not validate_status(status):
            return []
        filter_condition["status"] = status

    cursor = db.engine.dataset_info.find(filter_condition, {"_id": 0, "model_types": 0}).sort("created_at", -1)
    return await cursor.to_list(None)


async def delete_dataset(dataset_id: str) -> None:
    """Delete a dataset by dataset_id.

    Args:
        dataset_id (str): ID of the dataset to delete.
    """
    db.connect()
    await db.engine.dataset_info.delete_one({"dataset_id": dataset_id})
    await db.engine.datasets.delete_many({"dataset_id": dataset_id})


async def build_match_query_with_filter(dataset_id: str, filter_value: Dict[str, Any]) -> Dict[str, Any]:
    """매치 쿼리를 구성하는 함수"""
    match_query = {"$match": {"dataset_id": dataset_id}}
    if "metas" in filter_value and isinstance(filter_value["metas"], list):
        metas: Dict[str, list] = {}
        for meta in filter_value["metas"]:
            key = find_meta_key(meta)
            if key:
                metas.setdefault(key, []).append(meta)
        filter_value = metas
        logger.debug(f"Get meta aggregation for dataset {dataset_id} with filter {filter_value}")
        dataset_file_ids = await apply_meta_filters(dataset_id, filter_value)
        match_query["$match"]["image_id"] = {"$in": dataset_file_ids}
    return match_query


def build_lookup_stage() -> Dict[str, Any]:
    """lookup 스테이지를 구성하는 함수"""
    return {
        "$lookup": {
            "from": "raw_files",
            "localField": "image_id",
            "foreignField": "id",
            "as": "raw_files_docs",
        }
    }


def export_dataset_files(datsaet_id: str, filename: str):
    """sync function from export_dataset_files_async

    Args:
        datsaet_id (str): dataset_id

    Returns:
        _type_: _description_
    """
    return asyncio.get_event_loop().run_until_complete(export_dataset_files_async(datsaet_id, filename, {}))


async def export_dataset_files_async(dataset_id: str, file_name: str, filter_value: dict):
    """Export dataset files to a CSV file."""
    db.connect()
    query = {"dataset_id": dataset_id, "per_page": 0}
    dataset_files, _ = await get_dataset_file_list_async(query, filter_value)

    # check plz
    if not dataset_files:
        return None, None

    if not file_name:
        dataset_info = await db.engine.dataset_info.find_one({"dataset_id": dataset_id}, {"_id": 0, "dataset_name": 1})
        if dataset_info and "dataset_name" in dataset_info:
            file_name = dataset_info["dataset_name"]
        else:
            file_name = dataset_id
    file_name = sanitize_filename(file_name) + ".json"
    logger.debug(f"Exporting dataset files to {file_name}")
    file_path = f"{conf.AIMMOCRE_WORKDIR}/{file_name}"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(dataset_files, f, ensure_ascii=False, indent=4)
    return file_path, file_name


def get_curation_data_combination_step():
    """_summary_

    Returns:
        _type_: _description_
    """
    return {
        "_id": 0,
        "dataset_id": 1,
        "file_id": "$raw_files_docs.id",
        "file_name": "$raw_files_docs.file_name",
        "file_size": "132121",
        "thumbnail_url": "$raw_files_docs.thumbnail_url",
        "image_url": "$raw_files_docs.image_url",
        "metas": {"$map": {"input": "$metas", "as": "meta", "in": "$$meta.value"}},
        "embedding": {
            "$arrayElemAt": [
                {
                    "$filter": {
                        "input": "$embeddings",
                        "as": "item",
                        "cond": {"$eq": ["$$item.name", "embedding"]},
                    }
                },
                0,
            ]
        },
        "curated_mask": {
            "$arrayElemAt": [
                {
                    "$filter": {
                        "input": "$embeddings",
                        "as": "item",
                        "cond": {"$eq": ["$$item.name", "curated_mask"]},
                    }
                },
                0,
            ]
        },
        "anomaly_score": {
            "$arrayElemAt": [
                {
                    "$filter": {
                        "input": "$embeddings",
                        "as": "item",
                        "cond": {"$eq": ["$$item.name", "anomaly_score"]},
                    }
                },
                0,
            ]
        },
        "similar_ids": {
            "$arrayElemAt": [
                {
                    "$filter": {
                        "input": "$embeddings",
                        "as": "item",
                        "cond": {"$eq": ["$$item.name", "similar_ids"]},
                    }
                },
                0,
            ]
        },
        "similar_distances": {
            "$arrayElemAt": [
                {
                    "$filter": {
                        "input": "$embeddings",
                        "as": "item",
                        "cond": {"$eq": ["$$item.name", "similar_distances"]},
                    }
                },
                0,
            ]
        },
        "created_at": 1,
    }


def get_dataset_raw_files_lookup_step():
    """_summary_

    Returns:
        _type_: _description_
    """
    return {
        "$lookup": {
            "from": "raw_files",
            "localField": "image_id",
            "foreignField": "id",
            "as": "raw_files_docs",
        }
    }


def get_curation_data_refine_step():
    """_summary_

    Returns:
        _type_: _description_
    """
    return {
        "dataset_id": 1,
        "file_id": 1,
        "file_name": 1,
        "file_size": 1,
        "thumbnail_url": 1,
        "image_url": 1,
        "metas": 1,
        "embeddings": "$embedding.value",
        "curated_mask": "$curated_mask.value",
        "anomaly_score": {"$toDouble": "$anomaly_score.value"},
        "similar_ids": "$similar_ids.value",
        "similar_distances": "$similar_distances.value",
        "created_at": 1,
    }


def get_dataset_file(dataset_id: str, file_id: str):
    return asyncio.get_event_loop().run_until_complete(get_dataset_file_async(dataset_id, file_id))


async def get_dataset_file_async(dataset_id: str, file_id: str):
    db.connect()
    match_query = {"$match": {"dataset_id": dataset_id, "image_id": file_id}}

    pipeline = [
        match_query,
        get_dataset_raw_files_lookup_step(),
        {"$unwind": "$raw_files_docs"},  # 조인 결과 배열 풀기
        {"$project": get_curation_data_combination_step()},
        {"$project": get_curation_data_refine_step()},
    ]
    return await db.engine.datasets.aggregate(pipeline).to_list(None)


def get_dataset_file_list_by_id(dataset_id: str):
    """sync function from get_dataset_file_list_async"""
    query = {"dataset_id": dataset_id}
    return asyncio.get_event_loop().run_until_complete(get_dataset_file_list_async(query, {}))


def get_dataset_file_list(query: dict, filter_value: dict):
    """sync function from get_dataset_file_list_async"""
    return asyncio.get_event_loop().run_until_complete(get_dataset_file_list_async(query, filter_value))


async def get_dataset_file_list_async(query: dict, filter_value: dict):
    """Retrieve a paginated list of dataset files based on the provided query and filter criteria.

    Args:
        query (dict): A dictionary containing query parameters. Expected keys are:
            - dataset_id (str): The ID of the dataset to query.
            - page (int, optional): The page number for pagination. Defaults to 1.
            - per_page (int, optional): The number of items per page for pagination. Defaults to 20.
            - sort (list of dict, optional): A list of dictionaries specifying the sort criteria,
              where each dictionary has 'field' and 'order' keys.
        filter_value (dict): A dictionary containing filter criteria to apply to the dataset query.


    Returns:
        tuple: A tuple containing:
            - list: A list of paginated dataset file results.
            - int: The total count of dataset files that match the query and filter criteria.

    """
    db.connect()
    dataset_id = query["dataset_id"]

    page = query.get("page", 1)
    per_page = query.get("per_page", 20)
    # sort_criteria = {item["field"]: item["order"] for item in query["sort"]}

    match_query = await build_match_query_with_filter(dataset_id, filter_value)

    pipeline = [
        match_query,
        get_dataset_raw_files_lookup_step(),
        {"$unwind": "$raw_files_docs"},  # 조인 결과 배열 풀기
        {
            "$facet": {
                "total_count": [{"$count": "count"}],
                "paged_results": [
                    {"$skip": (page - 1) * per_page if per_page > 0 else 0},
                    {"$limit": per_page if per_page > 0 else 999999999},
                    {"$project": get_curation_data_combination_step()},
                    {"$project": get_curation_data_refine_step()},
                ],
            }
        },
    ]

    async for result in db.engine.datasets.aggregate(pipeline):
        total_count = result["total_count"][0]["count"] if result["total_count"] else 0
        paged_results = result["paged_results"]
        return paged_results, total_count
    return [], 0


def find_meta_key(value: str):
    """메타 value를 기반으로 key를 찾습니다."""
    for key, values in META_TYPE.items():
        if value in values:
            return key
    return None


async def get_dataset_meta_aggregation(dataset_id: str, filter_value: dict):
    """_summary_

    Args:
        dataset_id (str): _description_
        filter_value (dict): Filters for querying items. Format: 'metas:rainy,daytime'

    Returns:
        _type_: _description_
    """
    db.connect()
    query = {"dataset_id": dataset_id}
    dataset_files = await db.engine.datasets.find(query, {"image_id": 1}).to_list(None)
    if dataset_files is None:
        return []
    dataset_file_ids = [d["image_id"] for d in dataset_files]
    if "metas" in filter_value and isinstance(filter_value["metas"], list):
        metas: Dict[str, list] = {}
        for meta in filter_value["metas"]:
            key = find_meta_key(meta)
            if key:
                metas.setdefault(key, []).append(meta)
        filter_value = metas.copy()
    logger.debug(f"Get meta aggregation for dataset {dataset_id} with filter {filter_value}")
    dataset_file_ids = await apply_meta_filters(dataset_id, filter_value)
    aggregation = await get_meta_count_aggregation(dataset_id, dataset_file_ids)
    return aggregation


async def apply_meta_filters(dataset_id: str, metas: dict):
    """메타 name/ value 기반의 image id를 필터링합니다."""
    db.connect()
    meta_filter_aggregation_pipeline = create_meta_filter_aggregation_pipeline(dataset_id, metas)
    cursor = db.engine.datasets.aggregate(meta_filter_aggregation_pipeline)
    result = await cursor.to_list(None)
    return [doc["image_id"] for doc in result]


def create_meta_filter_aggregation_pipeline(dataset_id: str, conditions: dict):
    """Create aggregation pipeline for meta filtering

    Create aggregation pipeline for filtering documents based on meta name and value.

    Args:
        dataset_id: 조회할 dataset id
        conditions: {
            'weather': ['rainy', 'clear'],
            'time': ['daytime'],
            ...
        }
    Returns:
        aggregation pipeline
    """
    add_fields_stage = {"$addFields": {}}
    match_conditions = []

    for name, values in conditions.items():
        condition_field_name = f"{name}_condition"
        # 각 메타 데이터 이름(name)과 값을 기반으로 필터를 생성합니다.
        add_fields_stage["$addFields"][condition_field_name] = {
            "$ifNull": [
                {
                    "$filter": {
                        "input": "$metas",
                        "as": "meta",
                        "cond": {"$and": [{"$eq": ["$$meta.name", name]}, {"$in": ["$$meta.value", values]}]},
                    }
                },
                [],
            ]
        }
        # 생성된 필터링 조건을 기반으로 문서를 매칭하는 조건을 추가합니다.
        match_conditions.append({"$gt": [{"$size": f"${condition_field_name}"}, 0]})

    pipeline = [
        {"$match": {"dataset_id": dataset_id}},
        add_fields_stage,
        {"$match": {"$expr": {"$and": match_conditions}}},
        {"$project": {"image_id": 1}},  # 필요한 경우 추가 필드를 포함시킬 수 있습니다.
    ]

    return pipeline


def create_meta_count_aggregation_pipeline(dataset_id: str, image_id_list: list):
    """_summary_

    Args:
        dataset_id (str): _description_
        image_id_list (list): _description_

    Returns:
        _type_: _description_
    """
    pipeline = [
        {"$match": {"dataset_id": dataset_id, "image_id": {"$in": image_id_list}}},
        {"$unwind": "$metas"},
        {"$group": {"_id": {"name": "$metas.name", "value": "$metas.value"}, "count": {"$sum": 1}}},  # 합계
        {"$sort": {"_id.name": 1, "_id.value": 1}},
    ]
    return pipeline


async def get_meta_count_aggregation(dataset_id: str, image_id_list: list):
    """메타별로 통계를 내어 반환합니다."""
    db.connect()
    pipeline = create_meta_count_aggregation_pipeline(dataset_id, image_id_list)
    results = await db.engine.datasets.aggregate(pipeline).to_list(None)
    aggregation = {key: {item: 0 for item in value} for key, value in META_TYPE.items()}
    for result in results:
        name = result["_id"]["name"]
        value = result["_id"]["value"]
        count = result["count"]
        aggregation[name][value] = count
    return camelize_top_level_keys(aggregation)


def camelize_string(s):
    parts = s.split("_")
    # 첫 부분을 제외하고 각 부분의 첫 글자만 대문자로 만듭니다.
    return "".join(part.capitalize() if i > 0 else part for i, part in enumerate(parts))


def camelize_top_level_keys(data):
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            new_key = camelize_string(key)  # 최상위 키만 변환
            new_dict[new_key] = value  # 값을 그대로 유지
        return new_dict
    else:
        # 최상위 수준이 딕셔너리가 아니면 변환 없이 반환
        return data
