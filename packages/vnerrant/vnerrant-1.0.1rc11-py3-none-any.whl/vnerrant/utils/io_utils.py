import codecs
import json
import os
import pickle
from pathlib import Path
from typing import *

import jsbeautifier
import jsonlines
import yaml

_path_created = {}
DEFAULT_ENCODING = "utf-8"


def _is_ascii(text: Text) -> bool:
    return all(ord(character) < 128 for character in text)


def write_text_file(
    content: Text,
    file_path: Union[Text, Path],
    encoding: Text = "utf-8",
    append: bool = False,
) -> None:
    """Writes text to a file.

    Args:
        content: The content to write.
        file_path: The path to which the content should be written.
        encoding: The encoding which should be used.
        append: Whether to append to the file or to truncate the file.

    """
    mode = "a" if append else "w"
    with open(file_path, mode, encoding=encoding) as file:
        file.write(content)


def dump_obj_as_json_to_file(filename: Union[Text, Path], obj: Any) -> None:
    """Dump an object as a json string to a file."""

    write_text_file(json.dumps(obj, indent=2), filename)


def write_json_beautifier(file_path: Text, dict_info: Union[List, Dict]) -> None:
    """
    Write the content from dictionary into file with a beautiful format

    Args:
        file_path (Text): The file path
        dict_info (Dict): Dict will be dumped

    Returns:

    """
    opts = jsbeautifier.default_options()
    opts.indent_size = 4
    dict_ = jsbeautifier.beautify(json.dumps(dict_info, ensure_ascii=False), opts)
    with codecs.open(file_path, "w", "utf-8") as f:
        f.write(dict_)


def load_json(file_path: Text) -> Union[Dict, List]:
    """
    Load content from json file

    Args:
        file_path (Text): json path

    Returns: a dictionary

    """
    with codecs.open(file_path, "r", "utf-8-sig") as f:
        config = json.load(f)

    return config


def load_jsonl(file_path: Text) -> Union[Dict, List]:
    """
    Load content from jsonlines file

    Args:
        file_path (Text): jsonlines path

    Returns: a list

    """
    with jsonlines.open(file_path) as f:
        data = [obj for obj in f]

    return data


def load_yaml(file_path: Text) -> Dict:
    """
    Load the content in yaml file

    Args:
        file_path (Text): A File path

    Returns: Dict from yaml file

    """
    with open(file_path, "r") as file:
        yaml_data = yaml.load(file, Loader=yaml.CLoader)
    return yaml_data


def load_csv(file_path: Text) -> List[Dict]:
    """
    Load the content in csv file

    Args:
        file_path (Text): A File path

    Returns: Dict from csv file

    """
    import pandas as pd

    df = pd.read_csv(file_path, keep_default_na=False)
    data = df.to_dict("records")
    return data


def load_context(file):
    with open(file, "rb") as f:
        data = pickle.load(f)
    return data


def save_context(data, file):
    with open(file, "wb") as f:
        pickle.dump(data, f)


def get_extension(filename):
    return os.path.splitext(filename)[1]


def get_all_files_in_directory(directory, extensions=None):
    """
    Returns a list of all files in a directory, optionally filtered by file
    Args:
        directory: the directory to search
        extensions: List of extensions to filter by. If None, return all files
            Examples: [".md", ".txt"]

    Returns:

    """

    extensions = extensions or []
    extensions = [extensions] if isinstance(extensions, str) else extensions
    new_extensions = []
    for ext in extensions:
        ext = f".{ext}" if not ext.startswith(".") else ext
        new_extensions.append(ext)

    files = [os.path.join(dirpath, file) for dirpath, dirnames, files in os.walk(directory) for file in files]
    filtered_files = []
    for file in files:
        if new_extensions and get_extension(file) in new_extensions:
            filtered_files.append(file)
        elif not new_extensions:
            filtered_files.append(file)
    return filtered_files
