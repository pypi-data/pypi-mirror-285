import os
import time
import subprocess
import psutil
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient
from IPython import get_ipython
from aimmocore import config as acc
import threading


class MongoDB:
    """Motor Client"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Check if already initialized
            self.manage_db = ManageDatabase()
            self.client = None
            self.initialized = True

    def connect(self, port: int = acc.default_local_db_port):
        self.client = AsyncIOMotorClient(f"mongodb://0.0.0.0:{port}")
        self.engine = self.client["aimmocore"]
        logger.debug("aimmocore-db connected")

    async def init_index(self):
        await self.engine.datasets.create_index([("dataset_id", 1), ("image_id", 1)])
        await self.engine.raw_files.create_index([("id", 1)])

    async def ping(self):
        try:
            if self.client is None:
                return False
            result = await self.client["admin"].command("ping")
            return result["ok"] == 1

        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def close(self):
        self.client.close()


class ManageDatabase:
    def __init__(self, port: int = acc.default_local_db_port, bootup_timeout: int = 10):
        self.port = port
        self.mongod_process = None
        self.bootup_timeout = bootup_timeout
        self._ensure_mongodb()

    def _ensure_mongodb(self):
        install_dir = os.path.join(os.path.expanduser("~"), ".aimmocore", "mongodb_installation", "mongodb")
        mongod_path = os.path.join(install_dir, "bin", "mongod")

        # Check if mongod exists, if not, install it
        if not os.path.exists(mongod_path):
            logger.debug("aimmocore-db not found. Installing MongoDB as aimmocore-db...")
            subprocess.call(["python", "-m", "aimmocore_db.install_mongodb"])

        # Check if mongod is running, if not, start it
        if not self._wait_for_mongodb():
            logger.debug("aimmocore-db not running. Starting aimmocore-db...")
            self._start_mongodb(mongod_path)

    def _is_mongod_running(self):
        """Check if mongod is running on the specified port."""
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            if proc.info["name"] == "mongod":
                cmdline_str = " ".join(proc.info["cmdline"])
                if f"--port {self.port}" in cmdline_str:
                    return True
        return False

    def _wait_for_mongodb(self):
        """Wait until MongoDB is running on the specified port or timeout."""
        start_time = time.time()
        while (time.time() - start_time) < self.bootup_timeout:
            if self._is_mongod_running():
                return True
            logger.debug("aimmocore-db is not running. Checking again...")
            time.sleep(5)  # Check every 5 seconds
        return False

    def _start_mongodb(self, mongod_path):
        """Start MongoDB server."""
        data_dir = os.path.join(os.path.dirname(mongod_path), "data")
        log_file = os.path.join(os.path.dirname(mongod_path), "mongod.log")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        command = [
            mongod_path,
            "--dbpath",
            data_dir,
            "--logpath",
            log_file,
            "--bind_ip",
            "0.0.0.0",
            "--port",
            str(self.port),
        ]

        in_container = os.environ.get("SDK_IN_CONTAINER", "false") == "true"
        if not in_container:
            logger.debug("SDK not in container, ")
            command.append("--fork")

        self.mongod_process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )

        logger.debug(f"MongoDB started on port {self.port} with data directory: {data_dir} and log file: {log_file}")
        ip = get_ipython()
        if ip is not None:
            logger.debug("SDK running under IPython. Registering post_execute event.")
            ip.events.register("post_execute", self._check_kernel_status)

    def _check_kernel_status(self):
        """Check if the kernel is shutting down and stop MongoDB if it is."""
        if self.mongod_process.poll() is None:
            logger.debug("mongod_process.poll() is none")
            # self._stop_mongodb()

    def _stop_mongodb(self):
        """Stop MongoDB server."""
        if self.mongod_process is not None:
            install_dir = os.path.join(os.path.expanduser("~"), ".aimmocore", "mongodb_installation", "mongodb")
            mongo_path = os.path.join(install_dir, "bin", "mongo")

            # Using mongo shell to shut down the server
            shutdown_command = f"{mongo_path} --eval \"db.getSiblingDB('admin').shutdownServer()\""

            try:
                subprocess.call(shutdown_command, shell=True)
                logger.debug("MongoDB has been stopped.")
            except Exception as e:  # pylint: disable=broad-except
                logger.error(f"Error stopping MongoDB: {e}")
