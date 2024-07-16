import os

AIMMOCRE_WORKDIR = os.path.join(os.path.expanduser("~"), ".aimmocore", "workdir")
CURATION_UPLOAD_ENDPOINT = "https://curation-dataset-upload.azurewebsites.net/api/curation/upload"
CURATION_STATUS_ENDPOINT = "https://curation-dataset-upload.azurewebsites.net/api/curation/status"
CURATION_AUTH_ENDPOINT = "https://curation-dataset-upload.azurewebsites.net/api/curation/auth"
THUMBNAIL_DIR = os.path.join(os.path.expanduser("~"), ".aimmocore", "thumbnails")
REQUEST_TIMEOUT = 10
default_local_db_port = 27817


def init_workspace():
    """Initialize workspace"""
    if not os.path.exists(AIMMOCRE_WORKDIR):
        os.makedirs(AIMMOCRE_WORKDIR, exist_ok=True)


def init_thumbnail_dir():
    """Initialize thumbnail directory"""
    if not os.path.exists(THUMBNAIL_DIR):
        os.makedirs(THUMBNAIL_DIR, exist_ok=True)


def get_database_dir():
    return os.path.join(os.path.dirname(__file__), "database")


def get_mongo_path():
    return os.path.join(os.path.dirname(__file__), "database", "mongodb")


def get_database_port():
    return 27817
