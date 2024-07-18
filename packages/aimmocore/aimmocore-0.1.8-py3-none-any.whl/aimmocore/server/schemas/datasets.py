from typing import List
from pydantic import Field, model_validator
from enum import Enum
from .base import CamelModel


class ProcessStatus(Enum):
    """Curation task Status"""

    PREPARING = "Preparing"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    ERROR = "Error"


class Dataset(CamelModel):
    """Default dataset schema"""

    dataset_id: str = Field(alias="datasetId")
    dataset_name: str = Field(alias="datasetName")
    status: str = Field(alias="status")
    applied_metas: List[str] = Field(alias="appliedMetas")
    embedding_model: str = Field(alias="embeddingModel")
    file_count: int = Field(alias="fileCount")
    created_at: int = Field(alias="createdAt")


class Thumbnail(CamelModel):
    """Thumbnail schema"""

    dataset_id: str = Field(alias="datasetId")
    file_id: str = Field(alias="fileId")
    thumbnail_url: str = Field(alias="thumbnailUrl")
    image_url: str = Field(alias="imageUrl")
    created_at: int = Field(alias="createdAt")


class ThumbnailPageList(CamelModel):
    """Thumbnail page list schema"""

    items: List[Thumbnail]
    page: int = Field(alias="page")
    per_page: int = Field(alias="perPage")
    total: int = Field(alias="total")


class DatasetList(CamelModel):
    items: List[Dataset]


class DatasetFile(CamelModel):
    dataset_id: str = Field(alias="datasetId")
    file_id: str = Field(alias="fileId")
    file_name: str = Field(alias="fileName")
    file_size: int = Field(alias="fileSize")
    file_type: str = Field("Image", title="File Type", alias="fileType")
    thumbnail_url: str = Field(alias="thumbnailUrl")
    image_url: str = Field(alias="imageUrl")
    metas: List = Field(alias="metas")
    embeddings: List[float] = Field(alias="embeddings")
    curated_mask: int = Field(alias="curatedMask")
    anomaly_score: float = Field(alias="anomalyScore")
    created_at: int = Field(alias="createdAt")

    @model_validator(mode="before")
    def replace_values(cls, values):
        """change wrong values to correct one"""
        values["metas"] = ["clear" if x == "sunny" else x for x in values["metas"]]
        return values


class DatasetFileList(CamelModel):
    items: List[DatasetFile]


class DatasetFilePageList(CamelModel):
    items: List[DatasetFile]
    page: int = Field(alias="page")
    per_page: int = Field(alias="perPage")
    total: int = Field(alias="total")


class Embeddings(CamelModel):
    file_id: str = Field(alias="fileId")
    thumbnail_url: str = Field(alias="thumbnailUrl")
    image_url: str = Field(alias="imageUrl")
    embeddings: List[float] = Field(alias="embeddings")
    curated_mask: int = Field(alias="curatedMask")
    anomaly_score: float = Field(alias="anomalyScore")


class EmbeddingsList(CamelModel):
    items: List[Embeddings]
