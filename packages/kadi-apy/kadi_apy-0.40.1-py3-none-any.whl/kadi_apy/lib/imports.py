# Copyright 2023 Karlsruhe Institute of Technology
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
import hashlib
import json
import os
import zipfile
from tempfile import TemporaryDirectory
from urllib.parse import unquote

import jsonref
from rdflib import DCTERMS
from rdflib import RDF
from rdflib import SH
from rdflib import XSD
from rdflib import Graph
from rdflib.collection import Collection as RDFCollection

from kadi_apy.lib.exceptions import KadiAPYInputError
from kadi_apy.lib.exceptions import KadiAPYRequestError
from kadi_apy.lib.helper import generate_identifier
from kadi_apy.lib.resources.collections import Collection
from kadi_apy.lib.resources.records import Record
from kadi_apy.lib.resources.templates import Template


def import_eln(manager, file_path):
    """Import an RO-Crate file following the "ELN" file specification."""
    with zipfile.ZipFile(file_path) as ro_crate, TemporaryDirectory() as tmpdir:
        if not (namelist := ro_crate.namelist()):
            raise KadiAPYInputError("Archive is empty.")

        # We assume the first path contains the root directory of the crate.
        root_dir = namelist[0].split("/")[0]
        metadata_file_name = "ro-crate-metadata.json"

        if f"{root_dir}/{metadata_file_name}" not in namelist:
            raise KadiAPYInputError("Missing metadata file in RO-Crate.")

        ro_crate.extractall(tmpdir)

        root_path = os.path.join(tmpdir, root_dir)
        metadata_file_path = os.path.join(root_path, metadata_file_name)

        try:
            with open(metadata_file_path, mode="rb") as metadata_file:
                metadata = json.load(metadata_file)
        except Exception as e:
            raise KadiAPYInputError("Error opening or parsing metadata file.") from e

        # Collect all entities in the JSON-LD graph.
        if (
            not isinstance((graph := metadata.get("@graph", [])), list)
            or not len(graph) > 0
        ):
            _raise_invalid_content("Graph is not an array or empty.")

        entities = {}

        for entity in graph:
            if isinstance(entity, dict) and "@id" in entity:
                entities[entity["@id"]] = entity

        if (metadata_file_entity := entities.get("ro-crate-metadata.json")) is None:
            _raise_invalid_content(
                f"Entity describing '{metadata_file_name}' is missing."
            )

        is_kadi4mat = False
        if (
            publisher_entity := metadata_file_entity.get("sdPublisher")
        ) is not None and isinstance(publisher_entity, dict):
            publisher_data = entities.get(publisher_entity.get("@id"), publisher_entity)
            publisher_name = publisher_data.get("name")

            if publisher_name == "Kadi4Mat":
                is_kadi4mat = True

        if (root_entity := entities.get("./")) is None:
            _raise_invalid_content("Root dataset missing in graph.")

        if not isinstance((root_parts := root_entity.get("hasPart", [])), list):
            _raise_invalid_content("Root parts are not an array.")

        collection_id = None

        # Create a collection if we have multiple entries in the root dataset.
        if len(root_parts) > 1:
            response = _create_resource(
                manager, Collection.base_path, {"title": root_dir}
            )
            collection_id = response.json()["id"]

        # If applicable, collect all link data so records contained in the crate can be
        # linked accordingly after their creation.
        record_links_data = {}

        # Import all datasets as records.
        for root_part in root_parts:
            if not isinstance(root_part, dict) or "@id" not in root_part:
                _raise_invalid_content("Root part is not an object or missing an @id.")

            if (dataset_entity := entities.get(root_part["@id"])) is None:
                _raise_invalid_content(f"Entity {root_part['@id']} missing in graph.")

            if dataset_entity.get("@type") != "Dataset":
                continue

            record_metadata = {
                "title": dataset_entity.get("name", dataset_entity["@id"]),
                "description": dataset_entity.get("text", ""),
            }

            # Try to support both lists and comma-separated values.
            if isinstance((keywords := dataset_entity.get("keywords")), list):
                record_metadata["tags"] = keywords
            elif isinstance(keywords, str):
                record_metadata["tags"] = keywords.split(",")

            response = _create_resource(manager, Record.base_path, record_metadata)
            record = manager.record(id=response.json()["id"])

            # Add the record to the collection, if applicable.
            if collection_id is not None:
                record.add_collection_link(collection_id)

            if not isinstance(
                (dataset_parts := dataset_entity.get("hasPart", [])), list
            ):
                _raise_invalid_content("Dataset parts are not an array.")

            # Import all files of the dataset.
            for dataset_part in dataset_parts:
                if not isinstance(dataset_part, dict) or "@id" not in dataset_part:
                    _raise_invalid_content(
                        "Dataset part is not an object or missing an @id."
                    )

                if (file_entity := entities.get(dataset_part["@id"])) is None:
                    _raise_invalid_content(
                        f"Entity {dataset_part['@id']} missing in graph."
                    )

                if file_entity.get("@type") != "File":
                    continue

                file_id = unquote(file_entity["@id"]).split("/", 1)[-1]
                file_path = os.path.realpath(os.path.join(root_path, file_id))

                # Ensure that the file path is contained within the root path in the
                # temporary directory.
                if os.path.commonpath([root_path, file_path]) != root_path:
                    _raise_invalid_content(f"Referenced file {file_path} is invalid.")

                file_name = file_entity.get("name", os.path.basename(file_path))
                file_description = file_entity.get("text", "")
                file_encoding_format = file_entity.get("encodingFormat", "")
                file_checksum = file_entity.get("sha256")

                if file_checksum:
                    checksum = hashlib.sha256()

                    with open(file_path, mode="rb") as f:
                        while True:
                            buf = f.read(1_000_000)

                            if not buf:
                                break

                            checksum.update(buf)

                    if checksum.hexdigest() != file_checksum:
                        raise KadiAPYInputError(
                            f"SHA256 checksum mismatch for '{file_id}'."
                        )

                record.upload_file(file_path, file_name, file_description)

                if (
                    is_kadi4mat
                    and file_encoding_format == "application/json"
                    and file_name == f'{dataset_entity.get("identifier")}.json'
                ):
                    record_id, link_data = _handle_kadi_json_export(file_path, record)
                    record_links_data[record_id] = {
                        "link_data": link_data,
                        "record": record,
                    }

        if record_links_data:
            for record_meta in record_links_data.values():
                record = record_meta["record"]
                links_data = record_meta["link_data"]

                for link_data in links_data:
                    # Only use outgoing links to avoid attempting to create duplicates.
                    if "record_to" in link_data:
                        prev_record_id = link_data["record_to"]["id"]

                        # Skip records that are not contained in the crate.
                        if prev_record_id not in record_links_data:
                            continue

                        new_record_id = record_links_data[prev_record_id]["record"].id

                        record.link_record(
                            new_record_id, link_data["name"], link_data["term"]
                        )


def _raise_invalid_content(msg):
    raise KadiAPYInputError(f"Invalid content in metadata file: {msg}")


def _handle_kadi_json_export(file_path, record):
    try:
        with open(file_path, mode="rb") as f:
            json_data = json.load(f)
    except Exception as e:
        raise KadiAPYInputError("Error opening or parsing JSON export file.") from e

    record.edit(
        extras=json_data.get("extras", []),
        license=json_data.get("license"),
        type=json_data.get("type"),
    )

    return json_data["id"], json_data.get("links", [])


def import_json_schema(manager, file_path, template_type):
    """Import JSON Schema file and create a template."""
    if template_type not in ["record", "extras"]:
        raise KadiAPYRequestError("Template type must be either 'record' or 'extras'")

    try:
        with open(file_path, mode="rb") as f:
            json_schema = jsonref.load(f)
    except Exception as e:
        raise KadiAPYInputError("Error opening or parsing JSON file.") from e

    template_data = {
        "title": json_schema.get(
            "title", os.path.basename(file_path).rsplit(".", 1)[0]
        ),
        "description": json_schema.get("description", ""),
        "type": template_type,
    }

    if not (properties := json_schema.get("properties", {})):
        raise KadiAPYInputError("Only objects are supported as top-level types.")

    extras = _json_schema_to_extras(properties)

    if template_type == "record":
        template_data["data"] = {"extras": extras}
    else:
        template_data["data"] = extras

    _create_resource(manager, Template.base_path, template_data)


JSON_SCHEMA_TYPE_MAPPING = {"boolean": "bool", "integer": "int", "number": "float"}


def _json_schema_to_extras(extras_schema):
    extras_list = []

    if isinstance(extras_schema, dict):
        properties = extras_schema.items()
    else:
        properties = enumerate(extras_schema)

    for key, value in properties:
        extras = {}

        if isinstance(key, str):
            extras["key"] = key

        if (extras_description := value.get("description")) is not None:
            extras["description"] = extras_description

        # We just use "string" as fallback type, as extras always need an explicit type.
        value_type = value.get("type", "string")

        if isinstance(value_type, list):
            value_type = value_type[0]

        if value_type in ["object", "array"]:
            extras["type"] = "dict" if value_type == "object" else "list"

            if value_type == "object":
                result = _json_schema_to_extras(value["properties"])
            else:
                items = value.get("items")

                if items is not None:
                    items = [items] if items else []
                    result = _json_schema_to_extras(items)
                else:
                    result = _json_schema_to_extras(value.get("prefixItems", []))

            extras["value"] = result

        else:
            if value_type == "string":
                extras["type"] = "date" if value.get("format") == "date-time" else "str"
            else:
                extras["type"] = JSON_SCHEMA_TYPE_MAPPING[value_type]

            if (default := value.get("default")) is not None:
                extras["value"] = default

            validation = {}

            if (options := value.get("enum")) is not None:
                if None in options:
                    options = options[:-1]

                validation["options"] = list(options)

            # This handling of the custom "unit" property only works for files exported
            # via Kadi.
            if (unit := value.get("unit")) is not None:
                extras["unit"] = unit.get("default")

            maximum = value.get("maximum")
            minimum = value.get("minimum")

            if maximum is not None or minimum is not None:
                validation["range"] = {"max": maximum, "min": minimum}

            if validation:
                extras["validation"] = validation

        extras_list.append(extras)

    return extras_list


def import_shacl(manager, file_path, template_type):
    """Import SHACL Shapes file and create a template."""
    if template_type not in ["record", "extras"]:
        raise KadiAPYRequestError("Template type must be either 'record' or 'extras'")

    try:
        graph = Graph()

        with open(file_path, mode="rb") as f:
            graph.parse(f)
    except Exception as e:
        raise KadiAPYInputError(
            "Error opening or parsing the SHACL shapes file."
        ) from e

    if (current_ref := graph.value(predicate=RDF.type, object=SH.NodeShape)) is None:
        raise KadiAPYInputError(
            "sh:NodeShape at the root is missing as an object with rdf:type."
        )

    template_data = {
        "title": str(
            graph.value(
                current_ref,
                DCTERMS.title,
                default=os.path.basename(file_path).rsplit(".", 1)[0],
            )
        ),
        "description": str(graph.value(current_ref, DCTERMS.description, default="")),
        "type": template_type,
    }

    extras = _shacl_to_extras(current_ref, graph)

    if template_type == "record":
        template_data["data"] = {"extras": extras}
    else:
        template_data["data"] = extras

    _create_resource(manager, Template.base_path, template_data)


XSD_TYPE_MAPPING = {
    XSD.integer: "int",
    XSD.int: "int",
    XSD.float: "float",
    XSD.decimal: "float",
    XSD.double: "float",
    XSD.boolean: "bool",
    XSD.dateTime: "date",
}


def _shacl_to_extras(current_ref, graph, visited=None):
    """SHACL to extra metadata."""
    extras_list = []

    if visited is None:
        visited = set()

    for node_shape in graph.objects(current_ref, SH.node):
        node_extras = _shacl_to_extras(node_shape, graph)
        extras_list.extend(node_extras)

    for extras_shape in graph.objects(current_ref, SH.property):

        if (extra_key := graph.value(extras_shape, SH.name)) is None:
            continue

        extra = {"key": extra_key, "type": "str", "value": None}

        if (term_iri := graph.value(extras_shape, SH.path)) is not None:
            extra["term"] = term_iri

        if (
            extras_description := graph.value(extras_shape, SH.description)
        ) is not None:
            extra["description"] = extras_description

        nested_shapes = list(
            graph.objects(extras_shape, SH.qualifiedValueShape)
        ) or list(graph.objects(extras_shape, SH.node))

        for nested_shape in nested_shapes:
            if nested_shape is not None and nested_shape not in visited:
                visited.add(nested_shape)
                # list type extra-metadata also handled as a dict
                # since both list and dict types use the same SHACL property.
                extra["type"] = "dict"
                result = _shacl_to_extras(nested_shape, graph, visited)
                extra["value"] = result

        if (value_type := graph.value(extras_shape, SH.datatype)) is not None:
            # We use "str" as fallback type, as extras always need an explicit type.
            extra["type"] = XSD_TYPE_MAPPING.get(value_type, "str")

            if (
                default_value := graph.value(extras_shape, SH.defaultValue)
            ) is not None:
                extra["value"] = default_value.value

            validation = {}

            if value_type == XSD.anyURI:
                validation["iri"] = True

            if (
                required := graph.value(extras_shape, SH.minCount)
            ) is not None and required.value >= 1:
                validation["required"] = True

            maximum = graph.value(extras_shape, SH.maxInclusive)
            minimum = graph.value(extras_shape, SH.minInclusive)

            if maximum is not None or minimum is not None:
                validation["range"] = {}

                if maximum is not None:
                    validation["range"]["max"] = maximum.value
                if minimum is not None:
                    validation["range"]["min"] = minimum.value

            if (options_node := graph.value(extras_shape, SH["in"])) is not None:
                options_list = RDFCollection(graph, options_node)
                validation["options"] = [option.value for option in options_list]

            if validation:
                extra["validation"] = validation

        extras_list.append(extra)

    return extras_list


def _create_resource(manager, base_path, metadata):
    base_identifier = generate_identifier(metadata["title"])
    metadata["identifier"] = base_identifier

    index = 1

    while True:
        response = manager._post(base_path, json=metadata)

        if response.status_code == 201:
            return response

        errors = response.json().get("errors", {})

        # Check if only the identifier was the problem and attempt to fix it.
        if "identifier" in errors and len(errors) == 1:
            suffix = f"-{str(index)}"
            metadata["identifier"] = f"{base_identifier[:50-len(suffix)]}{suffix}"

            index += 1
        else:
            raise KadiAPYRequestError(response.json())

        # Just in case, to make sure we never end up in an endless loop.
        if index > 100:
            break

    raise KadiAPYRequestError("Error attempting to create resource.")
