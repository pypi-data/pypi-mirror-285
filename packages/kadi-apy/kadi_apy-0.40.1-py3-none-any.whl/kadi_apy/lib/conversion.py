# Copyright 2024 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dateutil import parser


def json_to_kadi(data):
    """Convert plain JSON to a Kadi4Mat-compatible extra metadata structure.

    :param data: The JSON data to convert as dictionary, list or singular, primitive
        value.
    :return: The converted data as a list of extra metadata.
    """
    return _json_to_kadi(data)


def _json_to_kadi(data, nested_type=None):
    extras = []

    if isinstance(data, dict):
        data = data.items()
    elif isinstance(data, list):
        data = enumerate(data, start=1)
    else:
        data = enumerate([data], start=1)

    for key, value in data:
        if value is None:
            continue

        extra = {}

        if nested_type != "list":
            extra["key"] = str(key)

        if isinstance(value, (dict, list)):
            extra["type"] = "dict" if isinstance(value, dict) else "list"
            extra["value"] = _json_to_kadi(value, extra["type"])
        else:
            extra["type"] = type(value).__name__

            if extra["type"] == "str":
                try:
                    value = parser.parse(value).isoformat()
                    extra["type"] = "date"
                except:
                    pass

            extra["value"] = value

        extras.append(extra)

    return extras
