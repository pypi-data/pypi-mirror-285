# coding=utf-8
"""Main for aimmocore"""
import asyncio
import threading
import webbrowser
import uvicorn
from loguru import logger
from IPython import get_ipython
from aimmocore.server.app import app


def is_notebook():
    try:
        # Check if the IPython kernel is being used
        if "IPKernelApp" in get_ipython().config:
            return True
    except Exception:
        pass
    return False


def launch_viewer(viewer_port: int = 10321):
    """Launch dataset viewer

    Args:
        viewer_port (int, optional): Defaults to 10321.
    """
    config = uvicorn.Config(app, host="0.0.0.0", port=viewer_port, log_level="error")
    server = uvicorn.Server(config)

    # Detect environment to check if it's running in a Jupyter notebook
    def is_jupyter_notebook():
        try:
            shell = get_ipython().__class__.__name__
            if shell == "ZMQInteractiveShell":
                return True  # Jupyter notebook or Jupyter QtConsole
            elif shell == "TerminalInteractiveShell":
                return False  # IPython terminal
            else:
                return False
        except NameError:
            return False  # Not in IPython

    # 서버 실행 함수
    async def run_server():
        logger.info(f"Curation viewer is running on http://localhost:{viewer_port}/")
        await server.serve()

    if is_jupyter_notebook():

        def start_server():
            loop = asyncio.get_event_loop()
            loop.run_until_complete(run_server())

        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()
        webbrowser.open_new_tab(f"http://localhost:{viewer_port}/")
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_server())
