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


from typing import Any, Dict, List

from velocitas_lib import get_app_manifest


def get_interfaces_for_type(type: str) -> List[Dict[str, Any]]:
    """Return all interfaces for the given type.

    Args:
        type (str): The type string to look up.

    Returns:
        List: A list of interfaces of the given type.
    """
    manifest_data = get_app_manifest()

    interfaces = []
    for interface in manifest_data["interfaces"]:
        if interface["type"] == type:
            interfaces.append(interface)

    return interfaces
