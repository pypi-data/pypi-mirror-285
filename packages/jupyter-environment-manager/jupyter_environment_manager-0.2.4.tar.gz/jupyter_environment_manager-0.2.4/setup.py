# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
jupyter_environment_manager setup

"""

import json
import sys
from pathlib import Path

import setuptools

HERE = Path(__file__).parent.resolve()

# The name of the project
name = "jupyter_environment_manager"

lab_path = HERE / name.replace("-", "_") / "labextension"

# Representative files that should exist after a successful build
ensured_targets = [str(lab_path / "package.json"), str(lab_path / "static/style.js")]

package_data_spec = {name: ["*"]}

labext_name = "@qbraid/jupyter-environment-manager"

data_files_spec = [
    (
        "share/jupyter/labextensions/%s" % labext_name,
        str(lab_path.relative_to(HERE)),
        "**",
    ),
    ("share/jupyter/labextensions/%s" % labext_name, str("."), "install.json"),
    (
        "etc/jupyter/jupyter_server_config.d",
        "jupyter-config/nb-config",
        "jupyter_environment_manager.json",
    ),
    # For backward compatibility with notebook server
    (
        "etc/jupyter/jupyter_notebook_config.d",
        "jupyter-config/server-config",
        "jupyter_environment_manager.json",
    ),
]

long_description = (HERE / "README.md").read_text()

# Get the package info from package.json
pkg_json = json.loads((HERE / "package.json").read_bytes())
version = pkg_json["version"].replace("-alpha.", "a").replace("-beta.", "b").replace("-rc.", "rc")

setup_args = dict(
    name=name,
    version=version,
    url=pkg_json["homepage"],
    project_urls={
        "Documentation": "https://docs.qbraid.com/projects/lab/en/latest/lab/environments.html",
        "Bug Tracker": pkg_json["bugs"]["url"],
    },
    author=pkg_json["author"]["name"],
    author_email=pkg_json["author"]["email"],
    description=pkg_json["description"],
    license=pkg_json["license"],
    license_file="LICENSE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "jupyter_server>=1.6,<2",
        "jupyter_client~=7.1.0",
        "tornado>=6.1.0",
        "notebook<7",
        "qbraid-core>=0.1.13",
    ],
    zip_safe=False,
    include_package_data=True,
    python_requires=">= 3.9",
    platforms="Linux, Mac OS X, Windows",
    keywords=["IPython", "Jupyter", "JupyterLab"],
    classifiers=[
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: IPython",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Framework :: Jupyter :: JupyterLab :: 3",
        "Framework :: Jupyter :: JupyterLab :: Extensions",
    ],
)

try:
    from jupyter_packaging import get_data_files, npm_builder, wrap_installers

    post_develop = npm_builder(build_cmd="install:extension", source_dir="src", build_dir=lab_path)
    setup_args["cmdclass"] = wrap_installers(
        post_develop=post_develop, ensured_targets=ensured_targets
    )
    setup_args["data_files"] = get_data_files(data_files_spec)
except ImportError as e:
    import logging

    logging.basicConfig(format="%(levelname)s: %(message)s")
    logging.warning("Build tool `jupyter-packaging` is missing. Install it with pip or conda.")
    if not ("--name" in sys.argv or "--version" in sys.argv):
        raise e

if __name__ == "__main__":
    setuptools.setup(**setup_args)
