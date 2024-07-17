"""
Utilities for working with files
"""
import json
import os
from typing import Dict, List, Optional

import jsonschema
import yaml

from core_library.utilities.misc_utils import setup_console_logger

mds_logger = setup_console_logger()


def yaml_read_file(file_path: str) -> Dict:
    """
    Safely loads a yaml file into a dictionary

    :param file_path: path to the file
    :type file_path: str
    :return: yaml file as a dictionary
    :rtype: Dict
    """
    mds_logger.info(f"Loading YAML file: {file_path}")
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data


def yaml_validate_schema(yaml: Dict, schema: Dict) -> bool:
    """
    YAML Validate the file with a predefined JSON schema

    :param yaml: YAML data
    :type yaml: Dict
    :param schema: JSON Schema
    :type schema: Dict
    :raises e: Validation Error
    :return: True if pass
    :rtype: bool
    """
    try:
        jsonschema.validate(instance=yaml, schema=schema)
        mds_logger.info("YAML file passed validation")
    except jsonschema.ValidationError as e:
        mds_logger.error("YAML file failed validation")
        raise e
    else:
        return True


def get_files_directory(
    directory: str, file_extension: Optional[str] = None
) -> List[str]:
    """
    Get file paths from a directory recursively

    :param directory: path to check
    :type directory: str
    :param file_extension: file_extension to include
    :type file_extension: Optional[str]
    :return: List of file paths
    :rtype: List[str]
    """
    file_paths = []
    for root, dir, files in os.walk(directory):
        for file in files:
            if file_extension:
                if file.endswith(file_extension):
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)
            else:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)

    return file_paths


def json_read_file(file_path: str) -> Dict:
    """
    Reads a json file and returns the data in a dict

    :param file_path: file path
    :type file_path: str
    :return: data
    :rtype: Dict
    """
    with open(file_path) as f:
        data = json.load(f)
    return data
