# Copyright (c) 2023-2024 Contributors to the Eclipse Foundation
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

import json
import os
import sys
import re
import zipfile
from io import TextIOWrapper
from typing import Any, Dict, List, Optional

import requests


def get_valid_arch(arch: str) -> str:
    """Return a known architecture for the given `arch`.

    Args:
        arch (str): The architecture of the profile.

    Returns:
        str: valid architecture.
    """
    if "x86_64" in arch or "amd64" in arch:
        return "x86_64"
    elif "aarch64" in arch or "arm64" in arch:
        return "aarch64"

    raise ValueError(f"Unknown architecture: {arch}")


def require_env(name: str) -> str:
    """Require and return an environment variable.

    Args:
        name (str): The name of the variable.

    Raises:
        ValueError: In case the environment variable is not set.

    Returns:
        str: The value of the variable.
    """
    var = os.getenv(name)
    if not var:
        raise ValueError(f"Environment variable {name!r} not set!")
    return var


def get_workspace_dir() -> str:
    """Return the workspace directory."""
    return require_env("VELOCITAS_WORKSPACE_DIR")


def get_app_manifest() -> Dict[str, Any]:
    manifest_data = json.loads(require_env("VELOCITAS_APP_MANIFEST"))
    if isinstance(manifest_data, dict):
        return manifest_data
    elif isinstance(manifest_data, list) and isinstance(manifest_data[0], dict):
        return manifest_data[0]
    else:
        raise TypeError("Manifest must be a dict or array!")


def get_script_path() -> str:
    """Return the absolute path to the directory the invoked Python script
    is located in."""
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def get_package_path() -> str:
    """Return the absolute path to the package directory the invoked Python
    script belongs to."""
    return require_env("VELOCITAS_PACKAGE_DIR")


def get_project_cache_dir() -> str:
    """Return the project's cache directory.

    Returns:
        str: The path to the project's cache directory.
    """
    return require_env("VELOCITAS_CACHE_DIR")


def get_cache_data() -> Dict[str, Any]:
    """Return the data of the cache as Python object."""
    cache_data = json.loads(require_env("VELOCITAS_CACHE_DATA"))

    if not isinstance(cache_data, dict):
        raise TypeError("VELOCITAS_CACHE_DATA has to be a JSON object!")

    return cache_data


def get_log_file_name(service_id: str, runtime_id: str) -> str:
    """Build the log file name for the given service and runtime.

    Args:
        service_id (str): The ID of the service to log.
        runtime_id (str): The ID of the runtime to log.

    Returns:
        str: The log file name.
    """
    return os.path.join(get_workspace_dir(), "logs", runtime_id, f"{service_id}.log")


def get_programming_language() -> str:
    """Return the programming language of the project."""
    return require_env("language")


def create_log_file(service_id: str, runtime_id: str) -> TextIOWrapper:
    """Create a log file for the given service and runtime.

    Args:
        service_id (str): The ID of the service to log.
        runtime_id (str): The ID of the runtime to log.

    Returns:
        TextIOWrapper: The log file.
    """
    log_file_name = get_log_file_name(service_id, runtime_id)
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True)
    return open(log_file_name, "w", encoding="utf-8")


def download_file(uri: str, local_file_path: str) -> None:
    with requests.get(uri, timeout=30) as infile:
        os.makedirs(os.path.split(local_file_path)[0], exist_ok=True)
        with open(local_file_path, "wb") as outfile:
            for chunk in infile.iter_content(chunk_size=8192):
                outfile.write(chunk)


def is_uri(path: str) -> bool:
    """Check if the provided path is a URI.

    Args:
        path (str): The path to check.

    Returns:
        bool: True if the path is a URI. False otherwise.
    """
    return re.match(r"(\w+)\:\/\/(\w+)", path) is not None


def obtain_local_file_path(
    path_or_uri: str, download_path: Optional[str] = None
) -> str:
    """Return the absolute path to the file, specified by a absolute/relative local path or with an URI.

    Args:
        path_or_uri (str): Absolute/relative local path or URI.
        download_path (str): The path to download the file.

    Returns:
        str: The absolute path to the file.
    """
    if not is_uri(path_or_uri):
        if os.path.isfile(path_or_uri):
            return path_or_uri
        elif os.path.isfile(os.path.join(get_workspace_dir(), path_or_uri)):
            return os.path.join(get_workspace_dir(), path_or_uri)
        else:
            raise FileNotFoundError(f"File {path_or_uri} not found!")

    if download_path is None:
        download_path = os.path.join(
            get_project_cache_dir(), "downloads", path_or_uri.split("/")[-1]
        )
    if os.path.isfile(download_path):
        path, file = os.path.split(download_path)
        parts = file.split(".", 1)
        filename = f"{parts[0]}_1.{parts[1]}" if len(parts) > 1 else f"{parts[0]}_1"

        download_path = os.path.join(path, filename)

    download_file(path_or_uri, download_path)
    return download_path


def extract_zip(file_path: str, extract_to: str) -> str:
    """Extract a zip file.

    Args:
        file_path (str): The file path to the zip.
        extract_to (str): The file path to extract to.

    Raises:
        RuntimeError if the file_path is not a zip.

    Returns:
        str: The file path to the extracted top level folder.
    """
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

        return extract_to
    else:
        raise RuntimeError(f"{file_path!r} is not a zip file!")


def discover_files_in_filetree(tree_root: str, file_type: str) -> List[str]:
    """
    Recursively search for files with a specific file type under the tree root.

    Args:
        tree_root (str): The path to the tree root to search from.
        file_type (str): The file type that is searched for.

    Returns:
        List[str]: A list of file paths, relative to the search tree root.
    """
    files = []
    for dir, _, potential_files in os.walk(tree_root):
        for file in potential_files:
            if file.endswith(file_type):
                files.append(os.path.join(dir, file))
    return files
