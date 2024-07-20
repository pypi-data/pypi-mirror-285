# Copyright (c) 2024 Contributors to the Eclipse Foundation
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

from io import TextIOWrapper
from typing import Callable, List, Optional


def to_camel_case(snake_str: str) -> str:
    """Return a camel case version of a snake case string.

    Args:
        snake_str (str): A snake case string.

    Returns:
        str: A camel case version of a snake case string.
    """
    return "".join(x.capitalize() for x in snake_str.lower().split("-"))


def create_truncated_string(input: str, length: int) -> str:
    """Create a truncated version of input if it is longer than length.
    Will keep the rightmost characters and cut of the front if it is
    longer than allowed.

    Args:
        input (str): The input string.
        length (int): The allowed overall length.

    Returns:
        str: A truncated string which has len() of length.
    """
    if len(input) < length:
        return input

    return f"...{input[-length+3:]}"  # noqa: E226 intended behaviour


def replace_text_in_file(file_path: str, text: str, replacement: str) -> None:
    """Replace all occurrences of text in a file with a replacement.

    Args:
        file_path (str): The path to the file.
        text (str): The text to find.
        replacement (str): The replacement for text.
    """

    with open(file_path, mode="r+", encoding="utf-8") as file:
        file_text = file.readlines()
        replaced_text_list = replace_item_in_list(file_text, text, replacement)
        replaced_text = "".join(replaced_text_list)
        # replace old content
        file.seek(0)
        file.write(replaced_text)
        file.truncate()


def replace_item_in_list(
    text: List[str],
    matching_text: str,
    replacement: str = "",
    remove_empty: bool = False,
) -> List[str]:
    """Replace the whole line which matches the given text with a replacement.

    Args:
        text (List[str]): All text lines to replace lines within.
        text (str): The text to find the line with.
        replacement (str): The replacement for line.
        remove_empty (bool): If true and the replacement for a line is empty, the line will be removed.
    """
    buffer: List[str] = []
    for line in text:
        if matching_text in line:
            line = replacement

            is_removing_empty_line = remove_empty and line == ""
            if is_removing_empty_line:
                continue

        buffer.append(line)

    return buffer


def replace_text_area(
    text: List[str], start_occurence: str, end_occurence: str, replacement: str = ""
) -> List[str]:
    """Replace all occurrences of all text areas matching the parameters with a replacement.
    If the replacement for a line is empty, then the line will be removed.

    Args:
        text (List[str]): All text lines to replace text within.
        start_occurence (str): The starting line which matches the occurence for replacement text area.
        start_occurence (str): The ending line which matches the occurence for replacement text area.
        replacement (str): The replacement for text area.
    """
    buffer = []
    is_capturing = False

    for line in text:
        occurence_count = line.count(start_occurence)
        if not is_capturing:
            if occurence_count == 0:
                buffer.append(line)
            elif occurence_count == 1:
                is_capturing = True

            continue

        if end_occurence in line:
            is_capturing = False

            if replacement:
                buffer.append(replacement)

    return buffer


def capture_area_in_file(
    file: TextIOWrapper,
    start_line: str,
    end_line: str,
    map_fn: Optional[Callable[[str], str]] = None,
) -> List[str]:
    """Capture an area of a textfile between a matching start line (exclusive) and the first line matching end_line (exclusive).

    Args:
        file (TextIOWrapper): The text file to read from.
        start_line (str): The line which triggers the capture (will not be part of the output)
        end_line (str): The line which terminates the capture (will not be bart of the output)
        map_fn (Optional[Callable[[str], str]], optional): An optional mapping function to transform captured lines. Defaults to None.

    Returns:
        List[str]: A list of captured lines.
    """
    area_content: List[str] = []
    is_capturing = False
    for line in file:
        if line.strip() == start_line:
            is_capturing = True
        elif line.strip() == end_line:
            is_capturing = False
        elif is_capturing:
            line = line.rstrip()

            if map_fn:
                line = map_fn(line)

            area_content.append(line)
    return area_content
