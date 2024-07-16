# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Handlers for carrying out quantum jobs actions (enable, disable, etc.)

"""
import json
import logging
import sys
import threading
from pathlib import Path
from typing import Dict, Tuple, Union

import tornado
from notebook.base.handlers import APIHandler
from qbraid_core.services.environments import get_env_path, update_install_status, which_python
from qbraid_core.services.quantum import quantum_lib_proxy_state
from qbraid_core.services.quantum.proxy_braket import disable_braket, enable_braket
from qbraid_core.system.executables import python_paths_equivalent
from qbraid_core.system.packages import (
    extract_include_sys_site_pkgs_value,
    set_include_sys_site_pkgs_value,
)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def quantum_jobs_supported_enabled(slug: str) -> Tuple[bool, bool]:
    """Checks if quantum jobs are enabled in environment"""
    slug_path = get_env_path(slug)
    state = quantum_lib_proxy_state("braket", is_default_python=False, slug_path=slug_path)
    supported = state.get("supported", False)
    enabled = state.get("enabled", False)
    return supported, enabled


def flip_include_sys_packages(python_exe: Union[str, Path], pyvenv_cfg: Union[str, Path]) -> bool:
    """Whether to toggle include-system-site-packages value"""
    try:
        is_sys_python = python_paths_equivalent(python_exe, sys.executable)

        if is_sys_python:
            return False

        return extract_include_sys_site_pkgs_value(pyvenv_cfg)
    except Exception:  # pylint: disable=broad-exception-caught
        return False


def safe_set_include_sys_packages(*args) -> None:
    """Set include-system-site-packages value safely"""
    try:
        set_include_sys_site_pkgs_value(*args)
    except Exception:  # pylint: disable=broad-exception-caught
        pass


class QuantumJobsHandler(APIHandler):
    """Handler for quantum jobs actions."""

    @tornado.web.authenticated
    def get(self):
        """Gets quantum jobs status of environment."""
        slug = self.get_query_argument("slug")
        supported, enabled = quantum_jobs_supported_enabled(slug)
        status = {"supported": int(supported), "enabled": int(enabled)}
        self.finish(json.dumps(status))

    @tornado.web.authenticated
    def put(self):
        """Enable/disable quantum jobs in environment."""
        input_data = self.get_json_body()
        slug = input_data.get("slug")
        action = input_data.get("action")  # enable or disable
        slug_path = get_env_path(slug)
        update_install_status(slug_path, 0, 0)
        thread = threading.Thread(
            target=self.toggle_quantum_jobs,
            args=(
                action,
                slug,
                slug_path,
            ),
        )
        thread.start()

        data = {"success": True, "stdout": f"{action[:-1]}ing quantum jobs", "stderr": ""}
        self.finish(json.dumps(data))

    def toggle_quantum_jobs(
        self, action: str, slug: str, slug_path: Path
    ) -> Dict[str, Union[int, str]]:
        """
        Toggles quantum jobs functionality using subprocess.

        Args:
            action (str): The action to perform ('enable' or 'disable').
            slug (str): Identifier for the quantum job setting.

        Returns:
            dict: A dictionary with keys 'success' (0 or 1), 'stdout', and 'stderr'.
        """
        try:
            python_exe = which_python(slug)
            cfg = slug_path / "pyenv" / "pyvenv.cfg"
            flip_site_packages = flip_include_sys_packages(python_exe, cfg)

            _, enabled_in = quantum_jobs_supported_enabled(slug)
            success = False
            message = ""

            # Check if action is valid
            if action not in ["enable", "disable"]:
                message = "Invalid quantum jobs action. Must be 'enable' or 'disable'."

            # Check if action is necessary
            elif (action == "enable" and enabled_in) or (action == "disable" and not enabled_in):
                message = f"Quantum jobs are already {action}d."
                success = True

            # Perform the action
            else:

                if flip_site_packages:
                    safe_set_include_sys_packages(False, cfg)

                if action == "enable":
                    enable_braket(python_exe)
                elif action == "disable":
                    disable_braket(python_exe)

                if flip_site_packages:
                    safe_set_include_sys_packages(True, cfg)

                _, enabled_out = quantum_jobs_supported_enabled(slug)
                success = enabled_in != enabled_out
                if success:
                    message = f"Successfully {action}d Amazon Braket quantum jobs."
                else:
                    message = f"Failed to {action} Amazon Braket quantum jobs."

            update_install_status(slug_path, 1, 1, message=message)
        except Exception as err:  # pylint: disable=broad-exception-caught
            update_install_status(slug_path, 1, 1, message=err)

            if flip_site_packages:
                safe_set_include_sys_packages(True, cfg)
