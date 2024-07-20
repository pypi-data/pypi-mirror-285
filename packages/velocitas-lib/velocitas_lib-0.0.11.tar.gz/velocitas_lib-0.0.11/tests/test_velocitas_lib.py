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

# flake8: noqa: U100 unused argument (because of pytest.fixture)

import json
import os
import sys
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from velocitas_lib import (
    get_app_manifest,
    get_cache_data,
    obtain_local_file_path,
    get_package_path,
    get_script_path,
    get_workspace_dir,
    require_env,
    get_project_cache_dir,
)
from velocitas_lib.services import get_services


@pytest.fixture()
def set_test_env_var() -> str:
    os.environ["TEST"] = "test"
    return os.environ["TEST"]


@pytest.fixture()
def set_velocitas_workspace_dir() -> str:
    os.environ["VELOCITAS_WORKSPACE_DIR"] = "/test/vehicle-app-workspace"
    return os.environ["VELOCITAS_WORKSPACE_DIR"]


@pytest.fixture()
def set_velocitas_package_dir() -> str:
    os.environ["VELOCITAS_PACKAGE_DIR"] = "./tests/package"
    return os.environ["VELOCITAS_PACKAGE_DIR"]


@pytest.fixture()
def set_velocitas_cache_dir() -> str:
    os.environ["VELOCITAS_CACHE_DIR"] = "/test/cache"
    return os.environ["VELOCITAS_CACHE_DIR"]


@pytest.fixture()
def set_app_manifest() -> str:
    app_manifest = {"vehicleModel": {"src": "test"}}
    os.environ["VELOCITAS_APP_MANIFEST"] = json.dumps(app_manifest)
    return os.environ["VELOCITAS_APP_MANIFEST"]


@pytest.fixture()
def set_velocitas_cache_data() -> str:
    cache_data_mock = {"testPropA": "testValueA", "testPropB": "testValueB"}
    os.environ["VELOCITAS_CACHE_DATA"] = json.dumps(cache_data_mock)
    return os.environ["VELOCITAS_CACHE_DATA"]


@pytest.fixture()
def mock_filesystem(fs: FakeFilesystem) -> FakeFilesystem:
    fs.add_real_file(
        os.path.join(Path(__file__).resolve().parent, "package", "manifest.json")
    )
    return fs


def test_require_env__env_var_set__returns_env_value(set_test_env_var):  # type: ignore
    assert require_env("TEST") == "test"


def test_require_env__env_var_not_set__raises_ValueError():
    with pytest.raises(ValueError):
        require_env("TEST_ENV_NOT_SET")


def test_get_workspace_dir__returns_workspace_dir_path(set_velocitas_workspace_dir):  # type: ignore
    assert get_workspace_dir() == "/test/vehicle-app-workspace"


def test_get_app_manifest__app_manifest_set__returns_app_manifest_data(
    set_app_manifest,
):
    assert get_app_manifest()["vehicleModel"]["src"] == "test"


def test_get_app_manifest__missing_key__raises_KeyError(set_app_manifest):  # type: ignore
    with pytest.raises(KeyError):
        get_app_manifest()["vehicleModel"]["srcs"]


def test_get_app_manifest__no_app_manifest__raises_ValueError():
    os.environ["VELOCITAS_APP_MANIFEST"] = ""
    with pytest.raises(ValueError):
        get_app_manifest()


def test_get_script_path__returns_script_path():
    assert get_script_path() == os.path.dirname(os.path.realpath(sys.argv[0]))


def test_get_package_path__returns_package_path(set_velocitas_package_dir):
    assert get_package_path() == "./tests/package"


def test_get_cache_data__returns_cache_data(set_velocitas_cache_data):  # type: ignore
    assert get_cache_data()["testPropA"] == "testValueA"
    assert get_cache_data()["testPropB"] == "testValueB"


def test_get_services__no_overwrite_provided__returns_default_services(
    set_velocitas_package_dir,
    mock_filesystem: FakeFilesystem,
):
    os.environ["runtimeFilePath"] = "runtime.json"
    mock_filesystem.create_file(
        f"{get_package_path()}/runtime.json",
        contents='[ { "id": "service1", "config": [ { "key": "image", "value": "image-service1" } ] } ]',
    )

    all_services = get_services()

    assert len(all_services) == 1
    assert all_services[0].id == "service1"
    assert all_services[0].config.image == "image-service1"


def test_get_services__overwrite_provided__returns_overwritten_services(
    set_velocitas_package_dir,
    mock_filesystem: FakeFilesystem,
):
    os.environ["runtimeFilePath"] = "runtime.json"

    mock_filesystem.create_file(
        f"{get_package_path()}/runtime.json",
        contents='[ { "id": "service1", "config": [ { "key": "image", "value": "image-service1" } ] } ]',
    )
    mock_filesystem.create_file(
        f"{get_workspace_dir()}/runtime.json",
        contents='[ { "id": "my-custom-service", "config": [ { "key": "image", "value": "image-my-custom-service" } ] } ]',
    )

    all_services = get_services()

    assert len(all_services) == 1
    assert all_services[0].id == "my-custom-service"
    assert all_services[0].config.image == "image-my-custom-service"

    mock_filesystem.reset()


def test_obtain_local_file_path__absolute_local_path(set_velocitas_workspace_dir):
    root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    assert obtain_local_file_path(f"{root}/README.md") == f"{root}/README.md"


def test_obtain_local_file_path__relative_local_path(set_velocitas_workspace_dir):
    assert obtain_local_file_path("README.md") == "README.md"


def test_obtain_local_file_path__absolute_local_path_not_available(
    set_velocitas_workspace_dir,
):
    pytest.raises(
        FileNotFoundError,
        obtain_local_file_path,
        "/workspaces/velocitas-lib/README2.md",
    )


def test_obtain_local_file_path__relative_local_path_not_available(
    set_velocitas_workspace_dir,
):
    pytest.raises(FileNotFoundError, obtain_local_file_path, "README2.md")


def test_obtain_local_file_path__uri(set_velocitas_workspace_dir):
    assert (
        obtain_local_file_path(
            "https://raw.githubusercontent.com/eclipse-velocitas/velocitas-lib/main/README.md",
            "/workspaces/velocitas-lib/.pytest_cache/README.md",
        )
        == "/workspaces/velocitas-lib/.pytest_cache/README.md"
    )
    Path.unlink(Path("/workspaces/velocitas-lib/.pytest_cache/README.md"))


def test_obtain_local_file_path__uri_no_download_path(
    set_velocitas_cache_dir,
    mock_filesystem: FakeFilesystem,
):
    mock_filesystem.create_dir(get_project_cache_dir())
    assert (
        obtain_local_file_path(
            "https://raw.githubusercontent.com/eclipse-velocitas/velocitas-lib/main/README.md"
        )
        == "/test/cache/downloads/README.md"
    )
