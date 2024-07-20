import hashlib
import inspect
import json
import logging
import os
from functools import cache, wraps

from .serialize import StringOutput
from .store import cacheable, parse_function_arguments
from .types import cfg_as_strings, convertable_types, simple_type_annotation_to_type, valid_config_types


def help(description=None, notarun=False, hide=False):
    def inner(func):
        func.description = description
        func.notarun = notarun
        func.hide = False

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return inner


class Ingredient:
    search_path = None
    output_path = None
    read_only = False
    artifact_log = None

    def build(self):
        if hasattr(self, "cfg"):
            for val in self.cfg.values():
                # build values that are (1) individual ingredients or (2) ingredients inside a list
                # We use "if val is not None" rather than the more idiomatic "if val" check here (and elsewhere, like store.py)
                # to avoid calling self.__len__ on an object that has not been instantiated yet. Otherwise, classes that override
                # __len__ can run into problems here, since __len__ may not be ready to use yet.
                if val is not None and hasattr(val, "build"):
                    val.build()
                elif isinstance(val, list):
                    for subval in val:
                        if subval is not None and hasattr(subval, "build"):
                            subval.build()

    def warm(self):
        if hasattr(self, "cfg"):
            for val in self.cfg.values():
                if val is not None and hasattr(val, "warm"):
                    val.warm()
                elif isinstance(val, list):
                    for subval in val:
                        if subval is not None and hasattr(subval, "warm"):
                            subval.warm()

    def cache_dict(self):
        # LTODO Somehow I suspect this can be improved
        cfg = {
            k: (
                v.cache_dict()
                if hasattr(v, "cache_dict")
                else (
                    v.cache_str()
                    if hasattr(v, "cache_str")
                    else (
                        [
                            x.cache_dict() if hasattr(x, "cache_dict") else x.cache_str() if hasattr(x, "cache_str") else x
                            for x in v
                        ]
                        if isinstance(v, list)
                        else v
                    )
                )
            )
            for k, v in self.cfg.items()
        }
        return cfg

    def cache_str(self):
        if not hasattr(self, "_json_config"):
            self._json_config = json.dumps(self.cache_dict(), sort_keys=True)
        return self._json_config

    # LTODO do we need cache_dict, cache_str, and dict_config ?
    def dict_config(self):
        return {k: v.dict_config() if hasattr(v, "dict_config") else v for k, v in self.cfg.items()}

    @staticmethod
    def from_path(path, output_path=None, append_search_path=None):
        from .base import instantiate_object

        assert not path.endswith("config.json"), "pass the path to the directory, not the config.json file"
        with open(os.path.join(path, "config.json"), "rt", encoding="utf-8") as f:
            config = json.load(f)
        # LTODO is 'None' output_path the right default here, or should it be the path provided?
        # argument for None: writes are unintuitive when you run a command to "open" an ingredient you downloaded
        #   i.e., your commands are writing to a directory that you perceive to have just opened
        # argument for provided path: inexperienced/new users might be inefficient due to disabled caching
        #   (feels like a weak argument; users can learn, and may not happen in many situations, like when used as a dependency)

        search_path = [path]
        if append_search_path:
            search_path.extend(append_search_path)
        return instantiate_object(config, output_path=output_path, search_path=search_path)

    def set_paths(self, search_path, output_path, recurse=True, overwrite_existing=True):
        if overwrite_existing or not self.search_path:
            self.search_path = search_path
        if overwrite_existing or not self.output_path:
            self.output_path = output_path
        if recurse:
            for val in self.cfg.values():
                if val is not None and hasattr(val, "set_paths"):
                    val.set_paths(search_path, output_path, recurse=recurse, overwrite_existing=overwrite_existing)

    def caching_like(self, obj, recurse=True, overwrite_existing=True):
        self.set_paths(obj.search_path, obj.output_path, recurse=recurse, overwrite_existing=overwrite_existing)

    def main(self):
        print("got default ingredient main for:", self)

    @cacheable(StringOutput)
    def cfg_file(self):
        return "\n".join(list(cfg_as_strings(self.cfg)))

    def gather_commands(self, prefix=""):
        name = prefix
        if prefix:
            prefix += "."

        d = {
            "deps": {k: v.gather_commands(prefix=prefix + k) for k, v in self.cfg.items() if hasattr(v, "gather_commands")},
            "name": name,
            "cls": self.name,
            # we call getmembers on the cls rather than obj to avoid creating @cached_properties
            "cmds": [func for name, func in inspect.getmembers(self.__class__) if callable(func)],
        }
        return d

    def print_commands(self):
        from colorama import Fore, Style

        def command_line(func, prefix=""):
            if func.__name__.startswith("_") or (hasattr(func, "hide") and func.hide):
                return None

            description = f"{Style.DIM}: " + func.description if hasattr(func, "description") and func.description else ""
            cmd = prefix + "." + func.__name__ if prefix else func.__name__
            s = f"  {Fore.GREEN}{cmd}{Style.RESET_ALL}{description}{Style.RESET_ALL}"
            return s

        default_commands = {func for name, func in inspect.getmembers(Ingredient) if callable(func)}
        print(f"\n{Fore.YELLOW}Ingredient default commands:{Style.RESET_ALL}")
        for func in sorted(default_commands, key=lambda x: x.__name__):
            desc = command_line(func)
            if desc:
                print(desc)

        nxt = [self.gather_commands()]
        while nxt:
            d = nxt.pop()
            nxt.extend(list(d["deps"].values()))

            print(f"\n{Fore.YELLOW}" + (d["name"] + "=" if d["name"] else "") + d["cls"] + f" commands:{Style.RESET_ALL}")
            for func in d["cmds"]:
                if func not in default_commands and func.__name__ not in ("warm", "build"):
                    desc = command_line(func, prefix=d["name"])
                    if desc:
                        print(desc)

    @help("display the config", notarun=True)
    def print_config(self):
        lines = list(cfg_as_strings(self.cfg))
        print("\n".join(lines))

    def pretty_print_config(self):
        print("----- config -----")
        lines = []
        self._config_summary(lines)
        print("\n".join(lines))

    def _config_summary(self, lines, prefix=""):
        from colorama import Style

        # show name, followed by module config, followed by dependencies
        order = sorted(self.cfg.keys())
        for key in order:
            if key == "_cls":
                continue
            if hasattr(self.cfg[key], "_config_summary"):
                lines.append(f"{prefix}{key}:{Style.RESET_ALL}")
                childprefix = prefix + "    "
                self.cfg[key]._config_summary(lines, prefix=childprefix)
            else:
                # LTODO show docstrings in help
                # if key has a description
                #     lines.append(f"{prefix}{Style.DIM}# {options[key].description}{Style.RESET_ALL}")

                color = ""
                # LTODO change color for non-default values
                # if self.cfg[key] is not its default value
                # color = Fore.GREEN
                lines.append(f"{color}{prefix}{key} = {self.cfg[key]}{Style.RESET_ALL}")

    @help("start an IPython shell inside the ingredient", notarun=True)
    def shell(self):
        from IPython import embed

        header = f"self.cfg: {self.cfg}\n"
        header += f"dropping into self: {type(self)}"

        embed(header=header)

    # TODO remove this? can it cause issues when something tries to print(self) before the object tree is fully initialized?
    def __str__(self):
        cfgstr = json.dumps(self.cache_dict(), sort_keys=True)
        return f"Ingredient<{cfgstr}>"


def configurable(func):
    """This decorator parses __init__'s args & kwargs and stores them in a self.cfg dict.
    The keys come from the function signature, so default kwargs are present.
    """

    @wraps(func)
    def new_init(self, *args, **kwargs):
        if func.__name__ != "__init__":
            logging.getLogger(__name__).warning("@configurable decorator applied to a non-__init__ method: %s", func.__name__)
            assert not self.cfg, "would overwrite self.cfg"

        self.name = self.__module__ + "." + self.__class__.__name__
        self.cfg = {"_cls": self.name}

        # populate self.cfg with the arguments passed to the function, which is typically __init__
        bound_args, _, _ = parse_function_arguments(func, [self] + list(args), kwargs)
        for k, v in bound_args.items():
            if k == "self":
                continue

            self.cfg[k] = v

            # only Ingredients and primitive types can be fully configured, so warn if any arguments cannot be
            arg_type = func.__annotations__.get(k, "missing")
            arg_type = simple_type_annotation_to_type(arg_type)[2] if arg_type != "missing" else str
            if arg_type not in valid_config_types and arg_type not in convertable_types and not issubclass(arg_type, Ingredient):
                logging.getLogger(__name__).warning("argument is not an Ingredient or primitive config type: %s", k)

        func(self, *args, **kwargs)

    return new_init


class HashedFile(Ingredient):
    @configurable
    def __init__(self, filename):
        self.filename = filename

    @cache
    def cache_str(self):
        return hash_file(self.filename)


def hash_file(fn, chunksize=8192):
    file_hash = hashlib.sha256()

    with open(fn, "rb") as f:
        chunk = f.read(chunksize)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(chunksize)

    return file_hash.hexdigest()
