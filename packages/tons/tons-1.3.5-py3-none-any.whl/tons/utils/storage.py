import decimal
import glob
import json
import os
import platform
import shutil
from copy import deepcopy
from typing import Any, ByteString, Optional, Dict

import yaml

from .exceptions import StorageError

CONFIG_FILENAME = 'config.yaml'


def global_config_dir() -> str:
    """
    Note: does not check that the directory exists
    """
    home_folder = os.path.expanduser("~")
    platform_name = platform.system().lower()

    if platform_name == "linux" \
            or platform_name == "darwin" \
            or platform_name == "windows" \
            or platform_name == "freebsd":
        return os.path.join(home_folder, ".config", "tons")
    else:
        raise OSError("Your operating system is not supported yet")


def local_config_dir() -> str:
    """
    Note: does not check that the directory exists
    """
    return os.path.abspath('.tons')


def get_global_config_path() -> str:
    return os.path.join(global_config_dir(), CONFIG_FILENAME)


def get_custom_config_path() -> Optional[str]:
    """
    Select the custom configuration file path.

    If the environment variable `TONS_CONFIG_PATH` is set, it returns its value.
    Otherwise, it looks for a custom configuration file named 'config.yaml' in the current working directory under the
    '.tons' subdirectory. If the file exists, it returns its path.

    Returns:
        Optional[str]: The path to the custom configuration file, or None if not found.
    """
    env_config_path = os.environ.get('TONS_CONFIG_PATH')
    if env_config_path:
        return env_config_path
    custom_config_path = os.path.join(local_config_dir(), CONFIG_FILENAME)
    if os.path.exists(custom_config_path):
        return custom_config_path


def get_default_workdir() -> str:
    _local_config_dir = local_config_dir()
    if os.path.exists(_local_config_dir):
        return _local_config_dir
    return global_config_dir()


def read_yaml(filepath: str):
    with open(filepath) as f:
        try:
            return yaml.safe_load(f)
        except (yaml.scanner.ScannerError, PermissionError, FileNotFoundError) as e:
            raise StorageError(e)


def read_json(filepath: str):
    with open(filepath, "r") as f:
        return json.loads(f.read())


def read_bytes(filepath: str):
    with open(filepath, "rb") as f:
        return f.read()


def save_json(filepath: str, data: Any):
    ensure_parent_dir_exists(filepath)

    if not data:
        data = None

    with open(filepath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def replace_decimals(config_dict: Dict):
    """
    Recursively traverses a nested dictionary and replaces all Decimal values with strings in-place.

    This function is useful when saving dictionaries using `yaml.safe_dump()`, as it resolves the `RepresenterError`
    that occurs when attempting to dump Decimal type fields. By converting Decimals to strings, this function ensures
    smooth serialization without errors.

    Args:
        config_dict (dict): The dictionary to replace decimals in.

    Returns:
        None

    Note:
        - This function modifies the input dictionary in-place without creating a new one.
        - Decimal values are replaced with strings using the `str()` conversion function.

    References:
        - Information about the pyyaml issue can be found at: https://github.com/yaml/pyyaml/issues/255

    Example:
        config = {
            'key1': Decimal('1.23'),
            'key2': {
                'nested_key': Decimal('4.56')
            }
        }

        replace_decimals(config)

        # After the function call, the config dictionary will be modified as follows:
        # {
        #     'key1': '1.23',
        #     'key2': {
        #         'nested_key': '4.56'
        #     }
        # }

    """
    for key, value in config_dict.items():
        if isinstance(value, dict):
            replace_decimals(value)
        elif isinstance(value, decimal.Decimal):
            config_dict[key] = str(value)


def save_yaml(filepath: str, data: Dict):
    """
    Saves the given dictionary as YAML data to the specified file path.

    Args:
        filepath (str): The path to the file where the YAML data will be saved.
        data (dict): The dictionary containing the data to be saved as YAML.

    Raises:
        StorageError: if a PermissionError or FileNotFoundError occurs during the file write operation.

    Note:
        - The function uses the `deepcopy()` function to create a copy of the input dictionary to avoid modifying
          the original data.
        - Decimal values within the dictionary are replaced with strings using `replace_decimals()`
          function.
        - The `ensure_parent_dir_exists()` function is called to ensure that the parent directory of the file path
          exists.
        - If the data is empty, it is set to None before writing to the file.
        - The file is written using `yaml.safe_dump()` with the `default_flow_style` parameter set to False.
    """
    data = deepcopy(data)
    replace_decimals(data)

    ensure_parent_dir_exists(filepath)

    if not data:
        data = None

    try:
        with open(filepath, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False)
    except (PermissionError, FileNotFoundError) as e:
        raise StorageError(e)


def save_bytes(filepath: str, data: ByteString):
    ensure_parent_dir_exists(filepath)

    try:
        with open(filepath, 'wb') as f:
            f.write(data)
    except (PermissionError, FileNotFoundError) as e:
        raise StorageError(e)


def ensure_parent_dir_exists(filepath: str):
    """
    Ensures that the parent directory of the specified file path exists.

    If the parent directory does not exist, the function calls `ensure_dir_exists()` to create the necessary
    directories.

    Args:
        filepath (str): The file path for which the parent directory needs to be ensured.

    """
    dirname = os.path.dirname(filepath)
    if dirname:
        ensure_dir_exists(dirname)


def ensure_dir_exists(dirpath: str):
    """
    Ensures that the specified directory path exists.

    If the directory does not exist, the function creates it using `os.makedirs()` with the `exist_ok=True` parameter,
    allowing the function to run without raising an exception if the directory already exists.

    Args:
        dirpath (str): The directory path that needs to be ensured.

    """
    os.makedirs(dirpath, exist_ok=True)


def exists(path: str):
    return os.path.exists(path)


def get_filenames_by_ptrn(dir: str, pattern: str):
    return glob.glob(os.path.join(dir, pattern))


def copy_file(copy_from, copy_to):
    ensure_parent_dir_exists(copy_to)
    shutil.copyfile(copy_from, copy_to)
