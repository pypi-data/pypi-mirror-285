# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Handlers for checking and updating environment's state/status file(s).

"""

import json
import logging
import os
import sys

import tornado
from notebook.base.handlers import APIHandler
from qbraid_core.services.environments.paths import get_env_path
from qbraid_core.services.environments.state import install_status_codes

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class InstallStatusHandler(APIHandler):
    """Handler for checking environment's install status."""

    @tornado.web.authenticated
    def get(self):
        """Return codes describing environment's install status."""
        slug = self.get_query_argument("slug")
        data = install_status_codes(slug)
        if data["complete"] == 1 and data["success"] == 1:
            self.handle_successful_install(slug)
        self.finish(json.dumps(data))

    def handle_successful_install(self, slug: str) -> None:
        """Commands to execute after successfully installing environment."""
        slug_path = str(get_env_path(slug))

        try:
            # Create symlink from lib64 to lib
            self.create_lib64_symlink(slug_path)
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error("Error creating symlink for environment: %s", err)

    @staticmethod
    def create_lib64_symlink(slug_path: str) -> None:
        """Create symlink from lib64 to lib in virtual environment."""
        pyenv_lib = os.path.join(slug_path, "pyenv", "lib")
        pyenv_lib64 = os.path.join(slug_path, "pyenv", "lib64")

        def supports_symlink() -> bool:
            """Check if the current OS supports symlinks."""
            # POSIX compliant systems (Unix-like systems) support symlinks
            # Windows supports symlinks from Vista onwards, but creating them might require
            # administrator privileges unless Developer Mode is enabled on Windows 10 and later
            return os.name == "posix" or (sys.version_info >= (3, 2) and os.name == "nt")

        if os.path.exists(pyenv_lib) and not os.path.exists(pyenv_lib64) and supports_symlink():
            try:
                os.symlink(pyenv_lib, pyenv_lib64)
            except OSError as err:
                logging.error("Error creating symlink for environment: %s", err)
