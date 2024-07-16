# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Handlers for managing IPython kernels.

"""

import json
import os
import sys
from typing import List, Tuple

import tornado
from jupyter_client.kernelspec import KernelSpecManager
from notebook.base.handlers import APIHandler
from qbraid_core.services.environments.paths import DEFAULT_LOCAL_ENVS_PATH, get_env_path
from qbraid_core.system.executables import is_exe


def get_kernels() -> Tuple[KernelSpecManager, List[str]]:
    """Get list of all installed kernels with valid executables."""
    kernel_spec_manager = KernelSpecManager()
    kernelspec_dict = kernel_spec_manager.get_all_specs()

    kernels = []
    deprecated = ["python3_qbraid"]

    # kernelspec_dict.pop("python3", None)
    for k, v in kernelspec_dict.items():
        try:
            exe_path = v["spec"]["argv"][0]
            env_ok = is_exe(exe_path)
        except (KeyError, IndexError, TypeError):
            env_ok = False
        if not env_ok or k in deprecated:
            kernel_spec_manager.remove_kernel_spec(k)
        else:
            kernels.append(k)
    return kernel_spec_manager, kernels


class ToggleEnvKernelHandler(APIHandler):
    """Handler for activating/deactivating environment by adding/removing kernel."""

    @tornado.web.authenticated
    def post(self):
        """Activate/deactivate environment by adding/removing kernel"""
        input_data = self.get_json_body()
        slug = input_data.get("slug")

        slug_path = str(get_env_path(slug))
        kernels_path = os.path.join(slug_path, "kernels")
        kernel_spec_manager, kernels_list = get_kernels()
        for f in os.listdir(kernels_path):
            if f in kernels_list:
                # If kernel exists, remove it
                kernel_spec_manager.remove_kernel_spec(f)
            else:
                # If kernel doesn't exist, add it
                resource_path = (
                    sys.prefix
                    if not os.path.exists(os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), slug))
                    else os.path.join(os.path.expanduser("~"), ".local")
                )
                join_path_kernels = os.path.join(kernels_path, f)
                kernel_spec_manager.install_kernel_spec(join_path_kernels, prefix=resource_path)

        data = {}
        self.finish(json.dumps(data))
