# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Handlers for installing and uninstalling packages into/from virtual environments.

"""

import json
import logging
import os
import subprocess
import sys
import threading
from typing import List, Optional

import tornado
from notebook.base.handlers import APIHandler
from qbraid_core.services.environments.paths import (
    DEFAULT_LOCAL_ENVS_PATH,
    get_env_path,
    which_python,
)
from qbraid_core.services.environments.state import update_install_status
from qbraid_core.system.executables import python_paths_equivalent
from qbraid_core.system.packages import set_include_sys_site_pkgs_value

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class InstallPackagesHandler(APIHandler):
    """Handler for installing packages into virtual environments."""

    @tornado.web.authenticated
    def post(self):
        """Install package in virtual environment."""
        input_data = self.get_json_body()
        slug = input_data.get("slug")
        package_lst = input_data.pop("packages", [])
        upgrade_pip = bool(input_data.pop("upgradePip", 0))
        system_site_packages = bool(input_data.pop("systemSitePackages", 1))

        res_data = {}
        if len(package_lst) == 0 and upgrade_pip is False:
            res_data["status"] = 200
            res_data["message"] += "No package(s) provided."
        else:
            res_data["status"] = 202
            res_data["message"] = "Started pip installs"
            slug_path = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), slug)
            update_install_status(slug_path, 0, 0)
            thread = threading.Thread(
                target=self.install_packages,
                args=(
                    slug,
                    slug_path,
                    package_lst,
                    upgrade_pip,
                    system_site_packages,
                ),
            )
            thread.start()
        self.finish(json.dumps(res_data))

    @staticmethod
    def install_packages(
        slug: str,
        slug_path: str,
        packages: List[str],
        upgrade_pip: Optional[bool] = False,
        system_site_packages: Optional[bool] = True,
    ) -> None:
        """Install packages in virtual environment."""
        python = which_python(slug)
        install_msg = ""

        if upgrade_pip:
            result = subprocess.run(
                [python, "-m", "pip", "install", "--upgrade", "pip"],
                capture_output=True,
                check=False,
            )
            stderr_msg = result.stderr.decode("utf-8")
            stdout_msg = result.stdout.decode("utf-8")
            install_msg += stderr_msg + stdout_msg.strip("\n").split("\n")[-1] + " "

        reqs_tmp = os.path.join(slug_path, "reqs_tmp.txt")
        install_command = [python, "-m", "pip", "install", "-r", reqs_tmp]
        with open(reqs_tmp, "w", encoding="utf-8") as file:
            for package in packages:
                file.write(package + "\n")

        if python_paths_equivalent(python, sys.executable):
            result = subprocess.run(install_command, capture_output=True, check=False)
        else:
            cfg = os.path.join(slug_path, "pyenv", "pyvenv.cfg")
            set_include_sys_site_pkgs_value(False, cfg)
            # Run the command and capture stderr
            result = subprocess.run(install_command, capture_output=True, check=False)
            if system_site_packages:
                set_include_sys_site_pkgs_value(True, cfg)
        stderr_msg = result.stderr.decode("utf-8")
        stdout_msg = result.stdout.decode("utf-8")
        install_msg += stderr_msg + stdout_msg.strip("\n").split("\n")[-1]
        try:
            os.remove(reqs_tmp)
        except FileNotFoundError as err:
            logging.error("Error removing tmp file: %s", err)
        update_install_status(slug_path, 1, 1, message=install_msg)


class UninstallPackageHandler(APIHandler):
    """Handler for uninstalling packages from virtual environments."""

    @tornado.web.authenticated
    def post(self):
        """Uninstall package in virtual environment."""
        input_data = self.get_json_body()
        slug = input_data.get("slug")
        package = input_data.pop("package", None)

        res_data = {}
        if package is None or len(package) == 0:
            res_data["status"] = 400
            res_data["message"] += "No package provided."
        else:
            res_data["status"] = 202
            res_data["message"] = "Started pip uninstall"
            slug_path = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), slug)
            update_install_status(slug_path, 0, 0)
            thread = threading.Thread(
                target=self.uninstall_package,
                args=(
                    slug,
                    package,
                ),
            )
            thread.start()
        self.finish(json.dumps(res_data))

    @staticmethod
    def uninstall_package(slug: str, package: str) -> None:
        """Uninstall package from virtual environment."""
        python = which_python(slug)
        slug_path = get_env_path(slug)
        result = subprocess.run(
            [python, "-m", "pip", "uninstall", package, "-y"], capture_output=True, check=False
        )
        stderr_msg = result.stderr.decode("utf-8")
        stdout_msg = result.stdout.decode("utf-8")
        uninstall_msg = stderr_msg + stdout_msg.strip("\n").split("\n")[-1]
        update_install_status(slug_path, 1, 1, message=uninstall_msg)
