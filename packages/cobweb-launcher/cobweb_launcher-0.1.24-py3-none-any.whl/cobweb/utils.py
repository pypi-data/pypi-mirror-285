import json
import re
import sys
from abc import ABC
from typing import Iterable
from importlib import import_module


def struct_table_name(table_name):
    return table_name.replace(".", "__p__").replace(":", "__c__")


def restore_table_name(table_name):
    return table_name.replace("__p__", ".").replace("__c__", ":")


def struct_queue_name(db_name, table_name):
    return sys.intern(f"__{db_name}_{table_name}_queue__")


def parse_info(info):
    if not info:
        return info

    if isinstance(info, dict):
        return info

    if isinstance(info, str):
        return json.loads(info)

    if isinstance(info, Iterable):
        result = list()
        for ii in info:
            if isinstance(ii, str):
                result.append(json.loads(ii))
            elif isinstance(ii, dict):
                result.append(ii)
            else:
                raise TypeError("must be in [str, dict]")

        return result


def struct_start_seeds(seeds):
    from .bbb import Seed
    if not seeds:
        return None
    if any(isinstance(seeds, t) for t in (list, tuple)):
        return [Seed(seed) for seed in seeds]
    elif any(isinstance(seeds, t) for t in (str, dict)):
        return Seed(seeds)


def issubclass_cobweb_inf(_class, inf_name):
    for _c in _class.__mro__[1:]:
        if _c.__name__ == inf_name:
            return True
    return False


def parse_import_model(model_info, model_type=None):
    if model_type not in ["scheduler", "storer"]:
        raise TypeError("model_type must be in scheduler, storer")
    if isinstance(model_info, str):
        if "import" in model_info:
            model_path, class_name = re.search(
                r"from (.*?) import (.*?)$", model_info
            ).groups()
            model = import_module(model_path)
            class_object = getattr(model, class_name)
        elif "." in model_info:
            info_list = model_info.split(".")
            class_name = info_list[-1]
            model_path = ".".join(info_list[:-1])
            model = import_module(model_path)
            class_object = getattr(model, class_name)
        else:
            model_path = f"cobweb.db.{model_type}.{model_info.lower()}"
            class_name = model_info.capitalize()
            model = import_module(model_path)
            class_object = getattr(model, class_name)
        return class_object, class_name
    elif issubclass(model_info, ABC):
        inf_name = model_type.capitalize() + "Interface"
        if issubclass_cobweb_inf(model_info, inf_name):
            return model_info, model_info.__name__
        raise ImportError()
    raise TypeError()


