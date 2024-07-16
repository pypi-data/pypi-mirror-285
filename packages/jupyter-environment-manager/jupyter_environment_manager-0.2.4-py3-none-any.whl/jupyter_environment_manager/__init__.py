# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Initialize the backend server extension

"""

import json
from pathlib import Path

from ._version import __version__
from .handlers import setup_handlers

# required for all labexes as of jlab 3
HERE = Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open() as fid:
    data = json.load(fid)


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": data["name"]}]


# only required for labexes that provision a server extension as well
def _jupyter_server_extension_paths():
    return [{"module": "jupyter_environment_manager"}]


def load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    server_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    url_path = "jupyter-environment-manager"
    setup_handlers(server_app.web_app, url_path)
    server_app.log.info(f"Registered jupyter_environment_manager extension at URL path /{url_path}")
