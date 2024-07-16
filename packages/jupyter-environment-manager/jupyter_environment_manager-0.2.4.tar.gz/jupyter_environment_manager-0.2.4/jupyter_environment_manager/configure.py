# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Handlers for managing user configurations and other local data.

"""

import configparser
import json
import logging
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import tornado
from notebook.base.handlers import APIHandler
from qbraid_core.config import USER_CONFIG_PATH
from qbraid_core.system.executables import is_valid_python

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class UserConfigHandler(APIHandler):
    """Handler for managing user configurations and other local data."""

    @tornado.web.authenticated
    def get(self):
        """Get locally stored credentials from qbraidrc."""
        credentials = self.read_qbraidrc()
        self.finish(json.dumps(credentials))

    def read_qbraidrc(self):
        """Read the qbraidrc file and return the contents as a dictionary."""
        config = configparser.ConfigParser()

        # Dictionary to store the results
        result = {
            "pythonVersion": self.get_python_version(),
            "email": os.getenv("JUPYTERHUB_USER"),
            "apiKey": os.getenv("QBRAID_API_KEY"),
            "refreshToken": os.getenv("REFRESH"),
            "url": "https://api.qbraid.com/api",
        }

        # Check if the file exists
        if not os.path.exists(USER_CONFIG_PATH):
            return result

        # Read the configuration file
        config.read(USER_CONFIG_PATH)

        # Extract email and refresh-token
        if "default" in config:
            result["url"] = config["default"].get("url", result["url"])
            result["email"] = config["default"].get("email", result["email"])
            result["apiKey"] = config["default"].get("api-key", result["apiKey"])
            result["refreshToken"] = config["default"].get("refresh-token", result["refreshToken"])

        return result

    @tornado.web.authenticated
    def post(self):
        """Save timestamp certificate file for isMount check."""
        home = os.getenv("HOME") or os.path.expanduser("~")

        # Get the current UTC datetime and format it as a string
        utc_now = datetime.utcnow()
        formatted_time = utc_now.strftime("%Y%m%d%H%M%S")

        # Define the filename and path
        directory = os.path.join(home, ".qbraid", "certs")
        filepath = os.path.join(directory, formatted_time)

        # Ensure the directory exists
        os.makedirs(directory, exist_ok=True)

        # Create an empty file
        with open(filepath, "w", encoding="utf-8"):
            pass  # The file is created and closed immediately

        thread = threading.Thread(target=self.delayed_file_delete, args=(filepath,))
        thread.start()

        self.finish(json.dumps({"filename": formatted_time}))

    def delayed_file_delete(self, filepath):
        """Delete a file."""
        time.sleep(5)
        try:
            Path(filepath).unlink()
        except (FileNotFoundError, OSError) as err:
            logging.error("Error deleting file: %s", err)

    @staticmethod
    def get_python_version(python_path: Optional[str] = None) -> str:
        """Gets the Python version of the given executable."""
        executable = python_path or sys.executable
        if not is_valid_python(executable):
            raise ValueError(f"Invalid Python executable: {executable}")

        try:
            result = subprocess.run(
                [executable, "--version"], capture_output=True, text=True, check=True
            )
            version = result.stdout.strip() or result.stderr.strip()
            return version
        except subprocess.CalledProcessError as err:
            raise RuntimeError(f"Failed to get Python version for {executable}") from err
