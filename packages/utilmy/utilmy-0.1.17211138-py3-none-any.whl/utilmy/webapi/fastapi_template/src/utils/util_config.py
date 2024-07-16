# -*- coding: utf-8 -*-
""" utils for config loading/ type checking
Doc::



"""
import json
import os
import pathlib
from typing import Dict, Union

import fire
import toml
import yaml

#########################################################################################################
from .util_log import log


##################################†#######################################################################
def to_file(txt: str, fpath: str, mode: str = "a"):
    with open(fpath, mode=mode) as fp:
        fp.write(txt)


#########################################################################################################
def config_load(
    config: Union[str, Dict, None] = None,
    to_dataclass: bool = True,
    config_field_name: str = None,
    environ_path_default: str = "config_path_default",
    path_default: str = None,
    config_default: dict = None,
    save_default: bool = False,
    verbose=0,
) -> dict:
    """Universal config loader: .yaml, .conf, .toml, .json, .ini .properties INTO a dict
    Doc::

        config_path:    str  = None,
        to_dataclass:   bool = True,  True, can access dict as dot   mydict.field
        config_field_name :  str  = Extract sub-field name from dict

        --- Default config
        environ_path_default: str = "config_path_default",
        path_default:   str  = None,
        config_default: dict = None,
        save_default:   bool = False,

       -- Priority steps
        1) load config_path
        2) If not, load in USER/.myconfig/.config.yaml
        3) If not, create default save in USER/.myconfig/.config.yaml
        Args:
            config_path:    path of config or 'default' tag value
            to_dataclass:   dot notation retrieval

            path_default :  path of default config
            config_default: dict value of default config
            save_default:   save default config on disk
        Returns: dict config
    """
    if isinstance(config, dict):
        return config

    else:
        config_path = config

    #########Default value setup ###########################################
    if path_default is None:
        default_val = str(os.path.dirname(os.path.abspath(__file__))) + "/myconfig/config.yaml"
        config_path_default = os.environ.get(environ_path_default, default_val)
        path_default = os.path.dirname(config_path_default)
    else:
        config_path_default = path_default
        path_default = os.path.dirname(path_default)

    if config_default is None:
        config_default = {"field1": "test", "field2": {"version": "1.0"}}

    #########Config path setup #############################################
    if config_path is None or config_path == "default":
        log(f"Config: Using {config_path_default}")
        config_path = config_path_default
    else:
        config_path = pathlib.Path(config_path)

    ######### Load Config ##################################################
    try:
        log("Config: Loading ", config_path)
        if config_path.suffix in {".yaml", ".yml"}:
            # Load yaml config file
            with open(config_path, "r") as yamlfile:
                config_data = yaml.load(yamlfile, Loader=yaml.FullLoader)

            if isinstance(config_data, dict):
                cfg = config_data
            else:
                dd = {}
                for x in config_data:
                    for key, val in x.items():
                        dd[key] = val
                cfg = dd

        elif config_path.suffix == ".json":
            cfg = json.loads(config_path.read_text())

        elif config_path.suffix in {".properties", ".ini", ".conf"}:
            from configparser import ConfigParser

            cfg = ConfigParser()
            cfg.read(str(config_path))

        elif config_path.suffix == ".toml":
            cfg = toml.loads(config_path.read_text())
        else:
            raise Exception(f"not supported file {config_path}")

        if config_field_name in cfg:
            cfg = cfg[config_field_name]

        if verbose >= 2:
            log(cfg)

        if to_dataclass:  ### myconfig.val  , myconfig.val2
            from box import Box

            return Box(cfg)
        return cfg

    except Exception as e:
        log(f"Config: Cannot read file {config_path}", e)

    ######################################################################
    log("Config: Using default config")
    log(config_default)
    if save_default:
        log(f"Config: Writing config in {config_path_default}")
        os.makedirs(path_default, exist_ok=True)
        with open(config_path_default, mode="w") as fp:
            yaml.dump(config_default, fp, default_flow_style=False)

    return config_default


#########################################################################################################
if __name__ == "__main__":
    fire.Fire()
