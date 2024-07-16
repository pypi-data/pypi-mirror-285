"""
AimmoCore: A Python package for aimmo core service

| Copyright 2024, AIMMO 
| "aimmo.ai <https://aimmo.ai/>"_
|
"""

import warnings
from .curation import Curation
from .config import get_database_dir, get_database_port, get_mongo_path, init_workspace, init_thumbnail_dir

init_workspace()
init_thumbnail_dir()

from .server.services.datasets import get_dataset_list, get_dataset_embeddings
from .main import launch_viewer


warnings.filterwarnings(action="ignore")
__all__ = [
    "config",
    "launch_viewer",
    "Curation",
    "get_database_dir",
    "get_database_port",
    "get_mongo_path",
    "get_dataset_list",
    "get_dataset_embeddings",
]
