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

import os

import pytest

from velocitas_lib import get_package_path, get_workspace_dir
from velocitas_lib.services import resolve_functions


@pytest.fixture()
def set_env_vars() -> None:
    os.environ["VELOCITAS_WORKSPACE_DIR"] = "./tests/project"
    os.environ["VELOCITAS_PACKAGE_DIR"] = "./tests/package"


def test_resolve_functions__unknown_function__raises_exception():
    with pytest.raises(RuntimeError, match="Unsupported function: 'foo'!"):
        resolve_functions("$foo( asd )")


def test_resolve_functions__pathInWorkspaceOrPackage__file_missing__raises_exception(
    set_env_vars,
):
    with pytest.raises(
        RuntimeError, match="Path 'asd' not found in workspace or package!"
    ):
        resolve_functions("$pathInWorkspaceOrPackage( asd )")


def test_resolve_functions__pathInWorkspaceOrPackage__file_exists_in_workspace():
    assert resolve_functions("$pathInWorkspaceOrPackage( foo.json )") == os.path.join(
        get_workspace_dir(), "foo.json"
    )


def test_resolve_functions__pathInWorkspaceOrPackage__file_exists_in_package(
    set_env_vars,
):
    assert resolve_functions(
        "$pathInWorkspaceOrPackage( manifest.json )"
    ) == os.path.join(get_package_path(), "manifest.json")
