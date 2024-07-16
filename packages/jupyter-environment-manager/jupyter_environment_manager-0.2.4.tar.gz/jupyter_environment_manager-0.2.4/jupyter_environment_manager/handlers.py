# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Module containing JupyterAPI routes and handlers.

"""

import os

from notebook.utils import url_path_join
from tornado.web import StaticFileHandler

from .configure import UserConfigHandler
from .devices import GPUStatusHandler
from .envs_create import CreateCustomEnvironmentHandler
from .envs_list import ListInstalledEnvironmentsHandler, PipListEnvironmentHandler
from .envs_pkgs import InstallPackagesHandler, UninstallPackageHandler
from .envs_remove import UninstallEnvironmentHandler
from .envs_state import InstallStatusHandler
from .jobs import QuantumJobsHandler
from .kernels import ToggleEnvKernelHandler


def setup_handlers(web_app, url_path):
    """Setup the JupyterAPI handlers for the jupyter_environment_manager."""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]

    # Prepend the base_url so that it works in a jupyterhub setting
    toggle_env_kernel_route = url_path_join(base_url, url_path, "toggle-kernel")
    list_installed_envs_route = url_path_join(base_url, url_path, "installed-environments")
    uninstall_env_route = url_path_join(base_url, url_path, "uninstall-environment")
    install_status_route = url_path_join(base_url, url_path, "install-status")
    create_custom_env_route = url_path_join(base_url, url_path, "create-custom-env")
    install_pkgs_route = url_path_join(base_url, url_path, "install-packages")
    uninstall_pkg_route = url_path_join(base_url, url_path, "uninstall-package")
    pip_list_env_route = url_path_join(base_url, url_path, "pip-freeze")
    quantum_jobs_route = url_path_join(base_url, url_path, "quantum-jobs")
    gpu_status_route = url_path_join(base_url, url_path, "gpu-status")
    user_config_route = url_path_join(base_url, url_path, "local-config")
    handlers = [
        (toggle_env_kernel_route, ToggleEnvKernelHandler),
        (list_installed_envs_route, ListInstalledEnvironmentsHandler),
        (uninstall_env_route, UninstallEnvironmentHandler),
        (install_status_route, InstallStatusHandler),
        (create_custom_env_route, CreateCustomEnvironmentHandler),
        (install_pkgs_route, InstallPackagesHandler),
        (uninstall_pkg_route, UninstallPackageHandler),
        (pip_list_env_route, PipListEnvironmentHandler),
        (quantum_jobs_route, QuantumJobsHandler),
        (gpu_status_route, GPUStatusHandler),
        (user_config_route, UserConfigHandler),
    ]

    web_app.add_handlers(host_pattern, handlers)

    doc_url = url_path_join(base_url, url_path, "static")
    doc_dir = os.getenv(
        "QBRAID_STATIC_DIR",
        os.path.join(os.path.dirname(__file__), "static"),
    )
    handlers = [(f"{doc_url}/(.*)", StaticFileHandler, {"path": doc_dir})]
    web_app.add_handlers(".*$", handlers)
