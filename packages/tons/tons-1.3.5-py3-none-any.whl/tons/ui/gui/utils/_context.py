from typing import Optional

from tons.config import init_config, Config
from tons.tonclient.utils import KeyStores, GlobalWhitelist
from tons.ui._utils import get_ton_client, get_ton_daemon, SharedObject


def init_shared_object_gui(*, specific_config_path: Optional[str] = None) -> SharedObject:
    config = init_config(specific_config_path)
    ton_client = get_ton_client(config)
    ton_daemon = get_ton_daemon(config, ton_client)
    ton_daemon.start()
    keystores = KeyStores(config.tons.keystores_path)
    whitelist = init_global_whitelist(config)

    ctx = SharedObject(config=config,
                       specific_config_path=specific_config_path,
                       ton_client=ton_client,
                       ton_daemon=ton_daemon,
                       keystores=keystores,
                       whitelist=whitelist)
    return ctx


def init_global_whitelist(config: Config):
    return GlobalWhitelist(config.tons.whitelist_path)
