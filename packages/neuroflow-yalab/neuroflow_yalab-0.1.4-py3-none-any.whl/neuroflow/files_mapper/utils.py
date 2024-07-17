"""
This module contains utility functions for working with files.
"""

import json
from pathlib import Path
from typing import Union


def load_json_file(file_path: Union[str, Path]):
    """
    Loads a JSON file and returns its contents as a Python dictionary.

    :param file_path: The path to the JSON file to be loaded.
    :return: A dictionary representing the contents of the JSON file.
    """
    file_path = Path(file_path)
    try:
        with Path.open(file_path, encoding="utf-8") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"The file {file_path} could not be decoded as JSON.")
