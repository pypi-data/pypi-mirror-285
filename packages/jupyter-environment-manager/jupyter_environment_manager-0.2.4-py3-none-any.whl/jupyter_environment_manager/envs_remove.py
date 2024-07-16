# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Handlers for uninstalling/removing environments.

"""

import json
import logging
import os
import shutil
import threading
import time

import tornado
from notebook.base.handlers import APIHandler
from qbraid_core.services.environments.paths import (
    DEFAULT_LOCAL_ENVS_PATH,
    get_next_tmpn,
    get_tmp_dir_names,
)
from qbraid_core.services.environments.state import install_status_codes

from .kernels import get_kernels

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class UninstallThreader:
    """Class for performing recursive removal of files and directories using multi-threading."""

    def __init__(self):
        self._counter = 0

    def counter(self) -> int:
        """Return the number of threads invoked."""
        return self._counter

    def remove(self, path: str) -> None:
        """Remove a file."""
        try:
            self._counter += 1
            os.remove(path)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def unlink(self, path: str) -> None:
        """Remove a symbolic link."""
        try:
            self._counter += 1
            os.unlink(path)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def rmtree(self, path: str) -> None:
        """Remove a directory and its contents."""
        try:
            self._counter += 1
            shutil.rmtree(path, ignore_errors=True)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def threaded_remove(self, src_path: str) -> None:
        """Remove files and directories using multi-threading."""
        if not os.path.isdir(src_path):
            return

        for filename in os.listdir(src_path):
            file_path = os.path.join(src_path, filename)
            if os.path.isfile(file_path):
                thread = threading.Thread(target=self.remove, args=(file_path,))
                thread.daemon = True
                thread.start()
            elif os.path.islink(file_path):
                thread = threading.Thread(target=self.unlink, args=(file_path,))
                thread.daemon = True
                thread.start()
            elif os.path.isdir(file_path):
                for nested_filename in os.listdir(file_path):
                    nested_filepath = os.path.join(file_path, nested_filename)
                    if os.path.isfile(nested_filepath):
                        thread = threading.Thread(target=self.remove, args=(nested_filepath,))
                        thread.daemon = True
                        thread.start()
                    elif os.path.islink(nested_filepath):
                        thread = threading.Thread(target=self.unlink, args=(nested_filepath,))
                        thread.daemon = True
                        thread.start()
                    elif os.path.isdir(nested_filepath):
                        thread = threading.Thread(target=self.rmtree, args=(nested_filepath,))
                        thread.daemon = True
                        thread.start()
                    else:
                        pass
            else:
                pass
        thread = threading.Thread(target=self.rmtree, args=(src_path,))
        thread.daemon = True
        thread.start()

    def join_threads(self) -> None:
        """Wait for all threads to complete."""
        main_thread = threading.current_thread()
        for thread in threading.enumerate():
            if thread is main_thread:
                continue
            thread.join()

    def reset_counter(self) -> None:
        """Reset the counter to 0."""
        self._counter = 0


class UninstallEnvironmentHandler(APIHandler):
    """Handler for uninstalling environments."""

    @tornado.web.authenticated
    def post(self):
        """Remove environment's kernels and change slug directory
        to tmp so it can be deleted in the background."""
        input_data = self.get_json_body()
        slug = input_data.get("slug")

        try:
            self.uninstall_env_kernels(slug)
        except Exception as err:  # pylint: disable=broad-exception-caught
            logging.error("Failed to remove kernel specs for %s: %s", slug, err)

        try:
            thread = threading.Thread(target=self.remove_env_cycle, args=(slug,))
            thread.start()

            status = 202
            message = f"Uninstalling environment {slug}."
            logging.info(message)
        except Exception as err:  # pylint: disable=broad-exception-caught
            status = 500
            message = f"Error uninstalling environment {slug}: {err}."
            logging.error(message)

        data = {"status": status, "message": message}
        self.finish(json.dumps(data))

    @staticmethod
    def uninstall_env_kernels(slug: str) -> None:
        """Remove environment's kernels from JupyterKernelSpecManager, if they exist."""
        kernelspec_path = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), slug, "kernels")

        if os.path.isdir(kernelspec_path):
            kernel_spec_manager, kernels_list = get_kernels()
            for f in os.listdir(kernelspec_path):
                if f in kernels_list:
                    kernel_spec_manager.remove_kernel_spec(f)

    @staticmethod
    def remove_env_cycle(slug: str) -> None:
        """Remove tmp directories in the background."""
        start = time.time()
        threader = UninstallThreader()
        slug_path = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), slug)
        tmpd_names = get_tmp_dir_names(DEFAULT_LOCAL_ENVS_PATH)
        status_codes = install_status_codes(slug)
        installing = status_codes.get("complete") == 0
        init_tmp_dirs = len(tmpd_names)
        num_cylces = 0
        sec_elapsed = 0

        while (
            num_cylces == 0
            or len(tmpd_names) > 0
            or installing
            and os.path.isdir(slug_path)
            and sec_elapsed < 60
        ):
            if os.path.isdir(slug_path) and (installing or num_cylces == 0):
                tmpn = get_next_tmpn(tmpd_names)
                rm_dir = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), tmpn)
                if installing:
                    os.makedirs(rm_dir, exist_ok=True)
                shutil.move(slug_path, rm_dir)
                tmpd_names.append(tmpn)
                if num_cylces == 0:
                    init_tmp_dirs += 1

            for tmpd_name in tmpd_names:
                tmpdir = os.path.join(str(DEFAULT_LOCAL_ENVS_PATH), tmpd_name)
                try:
                    threader.threaded_remove(tmpdir)
                except Exception as err:  # pylint: disable=broad-exception-caught
                    logging.error("Error removing directory %s: %s", tmpdir, err)

            # wait 5 seconds for each tmp rm to finish
            time.sleep(5)

            tmpd_names = get_tmp_dir_names(DEFAULT_LOCAL_ENVS_PATH)
            sec_elapsed = int(time.time() - start)
            num_cylces += 1

        num_threads = threader.counter()
        threader.join_threads()
        threader.reset_counter()

        logging.info(
            "Successfully uninstalled %d env(s) in %ds using %d threads "
            "over %d threaded remove cycles.",
            init_tmp_dirs,
            sec_elapsed,
            num_threads,
            num_cylces,
        )
