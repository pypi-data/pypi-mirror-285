# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Script for getting/bumping the next pre-release version.

"""

import pathlib
from typing import Union

from qbraid_core.system.versions import (
    compare_versions,
    extract_version,
    get_bumped_version,
    get_latest_package_version,
)

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()

PACKAGE_NAME = "jupyter_environment_manager"


def get_prelease_version(
    project_root: Union[pathlib.Path, str], package_name: str, shorten: bool = True
) -> str:
    """
    Determine the bumped version of a package based on local and latest versions.

    Args:
        project_root (pathlib.Path): Path to the project root directory.
        package_name (str): Name of the package to check.
        shorten (bool): Flag to determine if prerelease versions should be shortened.

    Returns:
        str: The bumped version string.

    """
    project_root = pathlib.Path(project_root)
    package_json_path = project_root / "package.json"

    if not package_json_path.exists():
        raise FileNotFoundError("package.json not found")

    v_local = extract_version(package_json_path, shorten_prerelease=shorten)
    v_latest_pre = get_latest_package_version(package_name, prerelease=True)
    v_latest_stable = get_latest_package_version(package_name, prerelease=False)
    v_latest = compare_versions(v_latest_pre, v_latest_stable)
    v_prerelease = get_bumped_version(v_latest, v_local)
    return v_prerelease


if __name__ == "__main__":

    v_prerelease = get_prelease_version(PROJECT_ROOT, PACKAGE_NAME, shorten=True)
    print(v_prerelease)
