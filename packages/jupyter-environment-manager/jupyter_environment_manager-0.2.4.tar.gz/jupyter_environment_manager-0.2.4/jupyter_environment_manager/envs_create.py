# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Handlers for creating custom environments.

"""

import base64
import json
import logging
import os
import re
import shutil
import sys
import threading
from pathlib import Path

import tornado
from jupyter_client.kernelspec import KernelSpecManager
from notebook.base.handlers import APIHandler
from qbraid_core.services.environments.create import create_local_venv
from qbraid_core.services.environments.paths import DEFAULT_LOCAL_ENVS_PATH
from qbraid_core.services.environments.state import update_install_status

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class CreateCustomEnvironmentHandler(APIHandler):
    """Handler for creating custom environments."""

    @tornado.web.authenticated
    def post(self):
        """Create a new qBraid environment."""
        input_data = self.get_json_body()
        slug = input_data.get("slug")
        prompt = input_data.get("prompt")
        display_name = input_data.get("kernelName")
        image_data_url = input_data.get("image")
        slug_path = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), slug)
        local_resource_dir = os.path.join(slug_path, "kernels", f"python3_{slug}")
        os.makedirs(local_resource_dir, exist_ok=True)

        try:
            # create state.json
            update_install_status(slug_path, 0, 0)

            # create python venv
            thread = threading.Thread(target=create_local_venv, args=(slug_path, prompt))
            thread.start()

            # create kernel.json
            kernel_json_path = os.path.join(local_resource_dir, "kernel.json")
            kernel_spec_manager = KernelSpecManager()
            kernelspec_dict = kernel_spec_manager.get_all_specs()
            kernel_data = kernelspec_dict["python3"]["spec"]
            if sys.platform == "win32":
                python_exec_path = os.path.join(slug_path, "pyenv", "Scripts", "python.exe")
            else:
                python_exec_path = os.path.join(slug_path, "pyenv", "bin", "python")
            kernel_data["argv"][0] = python_exec_path
            kernel_data["display_name"] = display_name
            with open(kernel_json_path, "w", encoding="utf-8") as file:
                json.dump(kernel_data, file, indent=2)

            # copy/save kernel logo files
            if image_data_url:
                self.save_image_from_data_url(
                    image_data_url, os.path.join(local_resource_dir, "logo-64x64.png")
                )
            else:
                sys_resource_dir = kernelspec_dict["python3"]["resource_dir"]
                logo_files = ["logo-32x32.png", "logo-64x64.png", "logo-svg.svg"]
                for file in logo_files:
                    sys_path = os.path.join(sys_resource_dir, file)
                    loc_path = os.path.join(local_resource_dir, file)
                    if os.path.isfile(sys_path):
                        shutil.copy(sys_path, loc_path)

            res_data = {"status": 202, "message": "Custom env setup underway"}
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error("Error creating custom environment: %s", err)
            res_data = {"status": 500, "message": str(err)}
        self.finish(json.dumps(res_data))

    @staticmethod
    def save_image_from_data_url(data_url: str, output_path: str) -> None:
        """Save an image from a base64-encoded Data URL to a file."""
        # Extract base64 content from the Data URL
        match = re.search(r"base64,(.*)", data_url)
        if not match:
            raise ValueError("Invalid Data URL")

        image_data = base64.b64decode(match.group(1))

        # Ensure the output directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Write the image data to a file
        with open(output_path, "wb") as file:
            file.write(image_data)
