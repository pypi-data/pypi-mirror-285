# -*- coding: utf-8 -*-
""" utils for config loading/ type checking
Doc::



"""
import json
import os

import fire
import toml
import yaml

from src.utils.util_base import os_get_dirtmp
from src.utils.util_config import config_load

#########################################################################################################
from src.utils.util_log import log


#########################################################################################################
#########################################################################################################
def test1():
    """config_load test code"""
    flist = test_create_file(dirout=None)
    for xi in flist:
        cfg_dict = config_load(xi)
        if len(cfg_dict) > 2 or len(cfg_dict.get("database", dict())) > 2:
            log(str(xi) + ", " + str(cfg_dict) + "", "\n")
        else:
            raise Exception(f" dict is empty {xi}")

    ###  Add other test for config_load
    xi = flist[0]

    log("# test to_dataclass")
    cfg_dict = config_load(xi, to_dataclass=True)
    log(cfg_dict.details)
    assert (
        len(cfg_dict.details) == 4
    ), "FAILED -> config_load(); parameter to_dataclass doesn't work"

    log("\ntest config_field_name")
    cfg_dict = config_load(xi, config_field_name="details")
    assert len(cfg_dict) > 0, "FAILED -> config_load(); parameter config_field_name doesn't work"

    log("\nENV variables")
    path = "ztmp/config.yaml"
    os.environ["myconfig"] = path
    cfg_dict = config_load(None, environ_path_default="myconfig", save_default=True)
    assert len(cfg_dict) > 1, "FAILED -> config_load(); return value isn't expected"
    assert os.path.exists(os.path.abspath(path)), "FAILED -> config_load(); config wasn't saved"

    log("\ntest path_default and save_default")
    path = "ztmp/config.yaml"
    cfg_dict = config_load(None, path_default=path, save_default=True)
    assert len(cfg_dict) > 1, "FAILED -> config_load(); cfg_dict is empty"
    assert os.path.exists(os.path.abspath(path)), "FAILED -> config_load(); config wasn't saved"

    log("\ntest config_default")
    config_default = {
        "field1": "test config_default",
        "field2": {"version": "1.0"},
        "field3": "data",
    }
    cfg_dict = config_load(None, config_default=config_default)
    assert cfg_dict == config_default, "FAILED -> config_load(); return value isn't expected"


###############################################################################################
def to_file(txt, fpath, mode="a"):
    with open(fpath, mode=mode) as fp:
        fp.write(txt)


def test_create_file(dirout=None):
    dir_cur = os_get_dirtmp() if dirout is None else dirout

    ##### create file for test
    ddict = {
        "data": "test",
        "details": {"version": "1.0", "integer": 1, "float": 1.0, "boolean": True},
    }

    flist = []

    ##### create config.yaml
    with open(dir_cur + "/config.yaml", mode="w") as fp:
        ddict["list1"] = [1, 2]
        yaml.dump(ddict, fp, default_flow_style=False)
        flist.append(dir_cur + "/config.yaml")

    #### create config.json
    with open(dir_cur + "/config.json", mode="w") as fp:
        json.dump(ddict, fp, indent=3)
        flist.append(dir_cur + "/config.json")

    #### create config.conf
    # TODO: function config_load doesn't support conf files
    data_ini = """[APP]
            ENVIRONMENT = development
            DEBUG = False

            [DATABASE]
            USERNAME = root
            PASSWORD = p@ssw0rd
    """
    with open(dir_cur + "/config.conf", "w") as fp:
        fp.write(data_ini)
        flist.append(dir_cur + "/config.conf")

    #### create config.toml
    with open(dir_cur + "/config.toml", "w") as toml_file:
        toml.dump(ddict, toml_file)
        flist.append(dir_cur + "/config.toml")

    ### create  config.ini
    data_ini = """[APP]
            ENVIRONMENT = development
            DEBUG = False

            [DATABASE]
            USERNAME = root
            PASSWORD = p@ssw0rd
    """
    with open(dir_cur + "/config.ini", "w") as fp:
        fp.write(data_ini)
        flist.append(dir_cur + "/config.ini")

    ## create  config.properties
    properties = """[database]
            db.user=mkyong
            db.password=password
            db.url=localhost
    """
    with open(dir_cur + "/config.properties", "w") as fp:
        fp.write(properties)
        flist.append(dir_cur + "/config.properties")

    return flist


if __name__ == "__main__":
    fire.Fire()
