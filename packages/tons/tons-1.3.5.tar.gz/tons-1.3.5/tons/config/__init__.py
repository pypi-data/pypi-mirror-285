from typing import Any, List, Tuple, Union, Optional

from tons import settings
from tons.utils import storage
from ._config import ConfigLocation, Config
from ._exceptions import ConfigNotFoundError
from ._provider import ProviderConfig, TonNetworkEnum
from ._tons import TonsConfig, TonProviderEnum
from ._gui import GuiConfig, TonScannerEnum


def set_network(config: Config, config_location: str, network: TonNetworkEnum):
    update_config_field(
        config_location, "provider.dapp.network", network)


def __custom_config_path(specific_config_path: str) -> str:
    return specific_config_path or settings.CUSTOM_CONFIG_PATH


def init_config(specific_config_path: Optional[str] = None) -> Config:
    """
    Searches for and loads configuration files in the system, following this logic:

    - Global config is located in settings.GLOBAL_CONFIG_PATH.
    - Custom config is optional, and selected with the following priority (highest to lowest):
        1) specific_config_path, if specified.
        2) settings.CUSTOM_CONFIG_PATH, if specified.

    The configurations are then merged, with custom config parameters having higher priority,
    overriding values from the global config.

    Args:
        specific_config_path (str, optional): Config path to override the custom config path.

    Returns:
        Config: Config object representing the merged configuration.
    """

    config = Config()

    global_config = __get_config(settings.GLOBAL_CONFIG_PATH)
    if global_config is not None:
        config = __merge_configs(global_config, config)

    custom_config_path = __custom_config_path(specific_config_path)
    if custom_config_path:
        custom_config = __get_config(custom_config_path, raise_error=True)
        if custom_config is not None:
            config = __merge_configs(custom_config, config)

    return config


def unset_config_field(config_location: Union[str, ConfigLocation], name: str):
    config_path = __get_config_path_from_location(config_location)
    config = __get_config(config_path)

    if name not in Config.field_names() or config is None:
        return

    config_dict = config.to_nondefault_dict_without_field(name)
    storage.save_yaml(config_path, config_dict)


def update_config_field(config_location: Union[str, ConfigLocation], name: str, value: Any):
    config_path = __get_config_path_from_location(config_location)
    config = __get_config(config_path)
    if config is None:
        config = Config()

    config.update_value(name, value)
    storage.save_yaml(config_path, config.dict(exclude_unset=True))


def get_configs_with_origins(specific_config_path: str) -> Tuple[List[Config], List[str]]:
    configs = []
    origins = []

    custom_config_path = __custom_config_path(specific_config_path)

    for config_path in (settings.GLOBAL_CONFIG_PATH, custom_config_path):
        if not config_path:
            continue
        config = __get_config(config_path)
        if config is not None:
            configs.append(config)
            origins.append(config_path)

    return configs, origins


def get_config(config_location: Union[str, ConfigLocation]) -> Union[Config, None]:
    config_path = __get_config_path_from_location(config_location)

    return __get_config(config_path)


def __get_config(config_path: str, raise_error: bool = False) -> Union[Config, None]:
    if not storage.exists(config_path):
        if raise_error:
            raise ConfigNotFoundError(
                f"Incorrect config file path: {config_path}")
        return None

    new_config_dict = storage.read_yaml(config_path)
    if new_config_dict is None:
        return None

    return Config.parse_obj(new_config_dict)


def __merge_dicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(__merge_dicts(dict1[k], dict2[k])))
            else:
                yield (k, dict2[k])
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def __merge_configs(merge_to: Config, merge_from: Config) -> Config:
    merged = __merge_dicts(merge_from.dict(exclude_unset=True),
                           merge_to.dict(exclude_unset=True))

    return Config.parse_obj(merged)


def __get_config_path_from_location(config_location: Union[str, ConfigLocation]) -> str:
    if config_location == ConfigLocation.global_location:
        return settings.GLOBAL_CONFIG_PATH
    elif config_location == ConfigLocation.custom_location:
        return settings.CUSTOM_CONFIG_PATH
    else:
        return config_location


__all__ = [
    "set_network",
    "init_config",
    "unset_config_field",
    "update_config_field",
    "get_configs_with_origins",
    "get_config",
    "ConfigLocation",
    "Config",
    "ConfigNotFoundError",
    "ProviderConfig",
    "TonNetworkEnum",
    "TonsConfig",
    "TonProviderEnum",
    'TonScannerEnum'
]
