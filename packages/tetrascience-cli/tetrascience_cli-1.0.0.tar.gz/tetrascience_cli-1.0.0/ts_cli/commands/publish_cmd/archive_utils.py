import io
import json
import os
import zipfile
from pathlib import Path
from typing import Iterable, Union

import yaml

from ts_cli.config.artifact_config import ArtifactConfig
from ts_cli.config.util import (
    load_from_json_file_if_present,
    load_from_yaml_file_if_present,
)
from ts_cli.util.files import copy


def abs_path_relative_to(relative_path, relative_to):
    """
    Join the two paths, and then provide the absolute path
    :param relative_path:
    :param relative_to:
    :return:
    """
    return os.path.abspath(
        Path(
            Path(relative_to).expanduser(),
            Path(relative_path).expanduser(),
        )
    )


def some_match(path, patterns, relative_to):
    """
    Returns true if there is some pattern that points to the same path as `path`
    :param path:
    :param patterns:
    :param relative_to:
    :return:
    """
    absolute_path = abs_path_relative_to(relative_to=relative_to, relative_path=path)
    matches = map(
        lambda pattern: absolute_path
        == abs_path_relative_to(relative_path=pattern, relative_to=relative_to),
        patterns,
    )
    return any(matches)


def included(path, *, inclusions, exclusions, relative_to):
    """
    Return true if file is not excluded or is explicitly included
    :param path:
    :param inclusions:
    :param exclusions:
    :param relative_to:
    :return:
    """
    return (not some_match(path, exclusions, relative_to)) or some_match(
        path, inclusions, relative_to
    )


def iterate_directory_inclusions(
    path: Union[str, Path],
    *,
    exclusions: Iterable[str],
    inclusions: Iterable[str],
):
    """
    Yields the relative file path for every file that is included
    :param path:
    :param exclusions:
    :param inclusions:
    :return:
    """
    if included(".", inclusions=inclusions, exclusions=exclusions, relative_to=path):
        for root, folders, files in os.walk(path, topdown=True):
            removals = set()
            for folder in folders:
                local_path = os.path.join(root, folder)
                relative_path = os.path.relpath(local_path, path)
                if not included(
                    relative_path,
                    inclusions=inclusions,
                    exclusions=exclusions,
                    relative_to=path,
                ):
                    removals.add(folder)
            for removal in removals:
                folders.remove(removal)

            for file in files:
                local_path = os.path.join(root, file)
                relative_path = os.path.relpath(local_path, os.path.join(path))
                if included(
                    relative_path,
                    inclusions=inclusions,
                    exclusions=exclusions,
                    relative_to=path,
                ):
                    yield relative_path


def copy_included_files_to(
    *,
    src_dir: str,
    dst_dir: str,
    exclusions: Iterable[str],
    inclusions: Iterable[str],
):
    """
    Copies the included files from `src_dir` to `dst_dir`
    :param src_dir:
    :param dst_dir:
    :param exclusions:
    :param inclusions:
    :return:
    """
    for relative_path in iterate_directory_inclusions(
        path=src_dir, exclusions=exclusions, inclusions=inclusions
    ):
        copy(src=Path(src_dir, relative_path), dst=Path(dst_dir, relative_path))


def add_directory_to_archive(
    zip_archive: zipfile.ZipFile,
    path: Union[str, Path],
) -> zipfile.ZipFile:
    """
    Copies all files under `path` to the archive
    :param zip_archive:
    :param path:
    :return:
    """
    for root, _folders, files in os.walk(path, topdown=True):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, os.path.join(path))
            zip_archive.write(local_path, relative_path)
    return zip_archive


def update_manifest_fields(manifest: dict, artifact_config: ArtifactConfig):
    """
    Overwrites fields in the manifest dict with fields from the artifact configuration
    :param manifest:
    :param artifact_config:
    :return:
    """
    manifest["type"] = artifact_config.type
    manifest["namespace"] = artifact_config.namespace
    manifest["slug"] = artifact_config.slug
    manifest["version"] = artifact_config.version
    return manifest


def update_protocol_json(path: Path, manifest: dict) -> dict:
    """
    Adds all manifest fields to the protocol.json
    :param path:
    :param manifest:
    :return:
    """
    protocol = load_from_json_file_if_present(path)
    protocol = {
        **protocol,
        **manifest,
    }
    with open(path, "w") as file:
        file.write(json.dumps(protocol))
    return protocol


def update_protocol_yaml(path: Path, manifest: dict) -> dict:
    """
    Adds all manifest fields to the protocol.{yml,yaml}
    :param path:
    :param manifest:
    :return:
    """
    protocol = load_from_yaml_file_if_present(path)
    protocol = {
        **protocol,
        **manifest,
    }
    with open(path, "w") as file:
        yaml.dump(protocol, file)
    return protocol


def update_schema_json(path: Path, manifest: dict) -> dict:
    """
    Adds namespace/slug:version fields to the schema.json
    :param path:
    :param manifest:
    :return:
    """
    schema = load_from_json_file_if_present(path)
    schema = {
        **schema,
        "properties": {
            **schema.get("properties", {}),
            "@idsNamespace": {"const": manifest.get("namespace")},
            "@idsType": {"const": manifest.get("slug")},
            "@idsVersion": {"const": manifest.get("version")},
        },
    }
    with open(path, "w") as file:
        json.dump(schema, file)
    return schema


def update_expected_json(path: Path, manifest: dict) -> dict:
    """
    Adds namespace/slug:version to the expected.json
    :param path:
    :param manifest:
    :return:
    """
    expected = load_from_json_file_if_present(path)
    expected = {
        **expected,
        "@idsNamespace": manifest.get("namespace"),
        "@idsType": manifest.get("slug"),
        "@idsVersion": manifest.get("version"),
    }
    with open(path, "w") as file:
        json.dump(expected, file)
    return expected


def update_manifest(path: str, artifact_config: ArtifactConfig) -> dict:
    """
    Updates the manifest.json and writes it back to the artifact directory
    :param path:
    :param artifact_config:
    :return:
    """
    if Path(path, "manifest.json").exists():
        manifest = load_from_json_file_if_present(Path(path, "manifest.json"))
        manifest = update_manifest_fields(manifest, artifact_config)
        with open(Path(path, "manifest.json"), "w") as file:
            file.write(json.dumps(manifest))
        return manifest
    return {}


def update_protocol(path: str, manifest: dict) -> None:
    """
    Updates the protocol if it exists, and writes it back to the artifact directory
    :param path:
    :param manifest:
    :return:
    """
    if Path(path, "protocol.json").exists():
        update_protocol_json(Path(path, "protocol.json"), manifest)
    if Path(path, "protocol.yml").exists():
        update_protocol_yaml(Path(path, "protocol.yml"), manifest)
    if Path(path, "protocol.yaml").exists():
        update_protocol_yaml(Path(path, "protocol.yaml"), manifest)


def update_ids(path: str, manifest: dict) -> None:
    """
    Updates existing IDS files, and writes them back to the artifact directory
    :param path:
    :param manifest:
    :return:
    """
    if Path(path, "schema.json").exists():
        update_schema_json(Path(path, "schema.json"), manifest)
    if Path(path, "expected.json").exists():
        update_expected_json(Path(path, "expected.json"), manifest)


def compress_directory(directory: Union[str, Path]):
    """
    Adds the directory to a zip file, and return the zip file's bytes
    :param directory:
    :return:
    """
    print("Compressing...", flush=True)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_archive:
        add_directory_to_archive(
            zip_archive,
            directory,
        )
    return zip_buffer.getvalue()
