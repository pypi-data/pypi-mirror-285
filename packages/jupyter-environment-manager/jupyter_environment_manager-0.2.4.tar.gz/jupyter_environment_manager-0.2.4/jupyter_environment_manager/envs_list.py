# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Handlers for aggregating environment and package list data.

"""

import configparser
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from typing import List, Optional, Set

import tornado
from notebook.base.handlers import APIHandler
from qbraid_core.services.environments.paths import (
    DEFAULT_LOCAL_ENVS_PATH,
    get_default_envs_paths,
    get_env_path,
    get_next_tmpn,
    get_tmp_dir_names,
    which_python,
)
from qbraid_core.services.environments.state import install_status_codes
from qbraid_core.services.environments.validate import is_valid_slug
from qbraid_core.system.executables import is_valid_python, python_paths_equivalent
from qbraid_core.system.packages import set_include_sys_site_pkgs_value

from .jobs import quantum_jobs_supported_enabled
from .kernels import get_kernels

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def _uri_to_filepath(uri: str) -> str:
    """Convert a file URI to a local file path."""
    if uri.startswith("file://"):
        return uri[len("file://") :]
    raise ValueError(f"Invalid URI: {uri}")


def extract_short_hash(pip_freeze_line: str) -> str:
    """
    Extracts the 7-character shortened hash from a pip freeze output line that includes a Git path.

    Args:
        pip_freeze_line (str): A line from pip freeze output containing a Git path.

    Returns:
        str: The 7-character shortened Git hash.

    Raises:
        ValueError: If no valid Git hash is found in the input.
    """
    # Regular expression to find the git hash in the provided string
    match = re.search(r"@ git\+https://.*@([a-fA-F0-9]{40})", pip_freeze_line)

    if match:
        # Extract the full 40-character hash and return the first 7 characters
        full_hash = match.group(1)
        return full_hash[:7]

    # If no hash is found, raise an error
    raise ValueError("No valid Git hash found in the input.")


def _extract_package_version(pip_freeze_string: str) -> Optional[str]:
    """Extract the version of a package from a pip freeze string.
    Return None if the version cannot be extracted."""

    # semantic versioning pattern
    semver_pattern = r"(\d+\.\d+\.\d+)"
    match = re.search(semver_pattern, pip_freeze_string)
    if match:
        return match.group(1)

    # git repo editable mode install version pattern
    git_editable_pattern = (
        r"^-e\s+"
        r"git\+https:\/\/github\.com\/"
        r"[a-zA-Z0-9._-]+\/[a-zA-Z0-9._-]+\.git@"
        r"[a-fA-F0-9]{40}#"
        r"egg=[a-zA-Z0-9._-]+$"
    )
    if re.match(git_editable_pattern, pip_freeze_string):
        parts = pip_freeze_string.split("#egg=")
        return parts[0].split(" ", 1)[-1]

    try:
        return extract_short_hash(pip_freeze_string)
    except ValueError:
        pass

    try:
        # extract version from locally installed package setup file path
        maybe_uri = pip_freeze_string.split(" @ ")[1]
        filepath = _uri_to_filepath(maybe_uri).strip("\n")
        setup_cfg_path = os.path.join(filepath, "setup.cfg")
        config = configparser.ConfigParser()
        config.read(setup_cfg_path)
        return config.get("metadata", "version")
    except Exception as err:  # pylint: disable=broad-exception-caught
        logging.error("Error extracting package version: %s", err)
    return None


def _rewrite_requirements_file(file_path: str) -> None:
    with open(file_path, "r", encoding="utf-8") as file:
        requirements = file.readlines()

    updated_requirements = []

    for requirement in requirements:
        if requirement.strip() == "":
            continue

        if len(requirement.split(" ")) == 3 and "@" in requirement:
            package = requirement.split(" @ ")[0]
            if package is None or package.strip() == "":
                continue

            version = _extract_package_version(requirement)
            if version is None:
                version = requirement.split(" ")[-1].strip("\n")

            requirement = f"{package}=={version}\n"

        elif requirement.startswith("-e"):
            package = requirement.split("egg=")[-1].strip("\n")
            if package is None or package.strip() == "":
                continue

            version = _extract_package_version(requirement)
            if version is None:
                continue

            requirement = f"{package}=={version}\n"

        if "==" not in requirement:
            continue

        updated_requirements.append(requirement)

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(updated_requirements)


def get_pip_list(slug: str) -> List[str]:
    """Return packages in requirements.txt in list form.
    If file not found, return empty list."""
    slug_path = str(get_env_path(slug))
    reqs_txt = os.path.join(slug_path, "requirements.txt")

    pip_list = []

    if os.path.isfile(reqs_txt):
        with open(f"{reqs_txt}", "r", encoding="utf-8") as f:
            pip_lines = f.readlines()
        for line in pip_lines:
            pkg = line.strip("\n")
            pip_list.append(pkg)

    return pip_list


def put_pip_list(slug: str, system_site_packages: Optional[bool] = True) -> List[str]:
    """Update/insert requirements.txt and return pip list."""
    python = which_python(slug)
    if is_valid_python(python) and not python_paths_equivalent(python, sys.executable):
        slug_path = str(get_env_path(slug))
        cfg = os.path.join(slug_path, "pyenv", "pyvenv.cfg")
        reqs_txt = os.path.join(slug_path, "requirements.txt")
        set_include_sys_site_pkgs_value(False, cfg)
        with open(reqs_txt, "w", encoding="utf-8") as file:
            subprocess.run(
                [python, "-m", "pip", "freeze"],
                stdout=file,
                text=True,
                check=True,
            )
        _rewrite_requirements_file(reqs_txt)
        if system_site_packages:
            set_include_sys_site_pkgs_value(True, cfg)

    return get_pip_list(slug)


class PipListEnvironmentHandler(APIHandler):
    """Handler for managing environment package list data."""

    @tornado.web.authenticated
    def post(self):
        """Get pip list of environment."""
        input_data = self.get_json_body()
        slug = input_data.get("slug")
        system_site_packages = input_data.pop("systemSitePackages", None)
        system_site_packages_bool = (
            True if system_site_packages is None else bool(system_site_packages)
        )
        package_lst = put_pip_list(slug, system_site_packages=system_site_packages_bool)

        data = {}
        data["packages"] = package_lst

        self.finish(json.dumps(data))


class ListInstalledEnvironmentsHandler(APIHandler):
    """Handler for managing installed environment list data."""

    @tornado.web.authenticated
    def get(self):
        """Gets data surrounding installed environments including any installing
        environment, installed environments, active environments, and pip lists
        of all installed environments."""
        _, kernels_list = get_kernels()  # list of names of installed kernels

        # list of directories where environments can be installed
        envs_paths = get_default_envs_paths()
        env_dir_lst = [str(env_path) for env_path in envs_paths]
        uninstalling = self.uninstalling_envs()  # set of slugs currently being uninstalled

        installing = None  # name of currently installing, if any
        installed = []  # list of installed environments
        active = []  # list of active environments
        qjobs_supported = []  # list of environments with quantum jobs functionality
        qjobs_enabled = []  # list of environments with quantum jobs enabled
        sys_python = []  # environments for which $(which python) = sys.executable

        for env_dir_path in env_dir_lst:
            if not os.path.isdir(env_dir_path):
                continue  # Skip if the path is not a directory

            for slug in os.listdir(env_dir_path):
                slug_path = os.path.join(env_dir_path, slug)

                # Skip if the path is not a directory or if it's not a valid slug directory
                if not self.validate_slug_env(slug_path) or slug in uninstalling:
                    continue

                # Add to installed environments list
                installed.append(slug)

                env_python = which_python(slug)
                if python_paths_equivalent(env_python, sys.executable):
                    sys_python.append(slug)

                # Check if the environment is active
                if self.is_active(slug_path, kernels_list):
                    active.append(slug)

                # Initialize 'installing' status if it's None
                if installing is None:
                    installing = self.check_install_status(slug)

                # Check if quantum jobs are supported and/or enabled
                try:
                    supported, enabled = quantum_jobs_supported_enabled(slug)
                    if supported:
                        qjobs_supported.append(slug)
                        if enabled:
                            qjobs_enabled.append(slug)
                except Exception as err:  # pylint: disable=broad-exception-caught
                    logging.error("Error determining quantum jobs state: %s", err)

        installing = "" if installing is None else installing

        data = {
            "installed": installed,
            "active": active,
            "installing": installing,
            "quantumJobs": qjobs_supported,
            "quantumJobsEnabled": qjobs_enabled,
            "sysPython": sys_python,
        }

        self.finish(json.dumps(data))

    @staticmethod
    def uninstalling_envs() -> Set[str]:
        """Return set of environment slugs currently being uninstalled."""
        # Assuming local_qbraid_envs_path and get_tmp_dir_names are defined elsewhere.
        tmpd_names = get_tmp_dir_names(DEFAULT_LOCAL_ENVS_PATH)
        uninstalling = set()

        for tmpd_name in tmpd_names:
            tmpdir = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), tmpd_name)
            if os.path.isdir(tmpdir):
                uninstalling.update(os.listdir(tmpdir))

        return uninstalling

    @staticmethod
    def validate_slug_env(slug_path: str) -> bool:
        """
        Return True if slug_path is a valid environment directory, False otherwise.
        If directory name is a valid slug, but does not contain a persistent state/status
        file, then it is moved to a tmp directory to be uninstalled. This is mainly a backstop
        for cancel install environment.

        """
        if not os.path.isdir(slug_path):
            return False

        slug = os.path.basename(slug_path)
        if not is_valid_slug(slug):
            return False

        persistent_files = ["state.json", "install_status.txt"]
        if any(os.path.isfile(os.path.join(slug_path, file)) for file in persistent_files):
            return True

        if os.path.dirname(slug_path) == str(DEFAULT_LOCAL_ENVS_PATH):
            tmpd_names = get_tmp_dir_names(DEFAULT_LOCAL_ENVS_PATH)
            tmpn = get_next_tmpn(tmpd_names)
            rm_dir = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), tmpn)
            os.makedirs(rm_dir, exist_ok=True)
            shutil.move(slug_path, rm_dir)

        return False

    @staticmethod
    def check_install_status(slug: str) -> Optional[str]:
        """Return slug if environment is installing, None otherwise."""
        try:
            install_data = install_status_codes(slug)
            return slug if install_data.get("complete") == 0 else None
        except KeyError:
            logging.error("Missing 'complete' key in install data for slug: %s", slug)
            return None
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error("Error checking install status for slug: %s, Error: %s", slug, err)
            return None

    @staticmethod
    def is_active(slug_path: str, kernels_list: List[str]) -> bool:
        """Return True if any env kernel is in the kernel list, False otherwise."""
        try:
            env_kernels_dir = os.path.join(slug_path, "kernels")
            if not os.path.isdir(env_kernels_dir):
                return False

            for kernel in os.listdir(env_kernels_dir):
                if kernel in kernels_list:
                    return True
            return False
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error("Error checking if environment kernel is active: %s", err)
            return False
