import importlib
import inspect
import json
import logging
import os
import pickle
import sys

from .cli import config_list_to_dict, parse_args
from .ingredient import Ingredient
from .store import ReadOnlyException, parse_function_arguments
from .types import cast_dict_to_types


logger = logging.getLogger("fob")  # __name__ may be __main__ here


def name_to_cls(name):
    path = name.split(".")
    mod_str = ".".join(path[:-1])
    cls_str = path[-1]

    mod = importlib.import_module(mod_str)
    cls = getattr(mod, cls_str)
    return cls


def instantiate_object(config, search_path=None, output_path=None):
    assert "_cls" in config
    assert all(isinstance(k, str) for k in config)
    unknown_types_in_config = {
        k: type(v)
        for k, v in config.items()
        if not isinstance(v, (str, float, int, bool, dict, list, tuple, type(None), Ingredient))
    }
    if unknown_types_in_config:
        logger.warning("unknown types in config: %s", unknown_types_in_config)

    cls = name_to_cls(config["_cls"]) if isinstance(config["_cls"], str) else config["_cls"]
    logger.debug("instantiate_object %s with config: %s", cls, config)

    # cast types to those in the type annotation
    config = cast_dict_to_types(config, getattr(cls.__init__, "__annotations__", {}))

    # add default args into config, so that it describes exactly what is instantiated
    default_args = {k: v.default for k, v in inspect.signature(cls).parameters.items() if k != "self"}
    new_defaults = config.get("*", {})
    for k, v in new_defaults.items():
        if k in default_args:
            default_args[k] = v
    for k, v in default_args.items():
        if k not in config:
            config[k] = v

    # create the final config, which serves as kwargs, by calling instantiate_object to create any ingredients requested
    # first, separate the config keys corresponding to ingredients (dep_keys) from those that are primitives (string, int, etc)
    # TODO this breaks when a list of e.g. strings is passed (rather than a list of ingredients)
    newcfg = {
        k: v for k, v in config.items() if not isinstance(v, dict) and not isinstance(v, list) and not isinstance(v, Ingredient)
    }
    dep_keys = [k for k in config if k not in newcfg and k != "*"]

    # next, add the ingredients back into newcfg, handling the (1) Ingredient object and (2) config dict cases
    for k in dep_keys:
        if isinstance(config[k], Ingredient):
            # (1) we have an Ingredient object, so copy it over directly and set its cache paths
            newcfg[k] = config[k]
            # if either of the Ingredient's paths are None, set_paths will replace them with the path given to instantiate_object.
            # without this, default args like index=AnseriniIndex() will raise errors due to having output_path=None.
            config[k].set_paths(search_path=search_path, output_path=output_path, recurse=True, overwrite_existing=False)
        else:
            # (2) we have a config dict for an Ingredient, so use instantiate_object to create it
            # fall back to the default in case _cls was not specified because the default class was expected
            if "_cls" not in config[k]:
                if isinstance(default_args[k], Ingredient):
                    config[k]["_cls"] = default_args[k].__module__ + "." + default_args[k].__class__.__name__
                elif isinstance(default_args[k], list):
                    pass
                    # raise RuntimeError(f"cannot infer default _cls from list argument: {k}")
                else:
                    config[k]["_cls"] = default_args[k]["_cls"]

            if isinstance(config[k], list):
                newcfg[k] = []
                # TODO handle case where this is an Ingredient already
                for cfg_entry in config[k]:
                    depcfg = cfg_entry.copy()
                    if new_defaults:
                        depcfg["*"] = new_defaults
                    newcfg[k].append(instantiate_object(depcfg, search_path=search_path, output_path=output_path))
            else:  # dict
                depcfg = config[k].copy()
                if new_defaults:
                    depcfg["*"] = new_defaults
                newcfg[k] = instantiate_object(depcfg, search_path=search_path, output_path=output_path)

    # finally, use newcfg as kwargs and instantiate cls
    kwargs = {k: v for k, v in newcfg.items() if k != "_cls"}
    obj = cls(**kwargs)
    obj.search_path = search_path
    obj.output_path = output_path
    return obj


def log_handler():
    import colorlog

    fmt = "%(thin_white)s%(asctime)s - %(reset)s%(log_color)s%(levelname)s - %(name)s.%(funcName)s - %(message)s"
    sh = colorlog.StreamHandler()
    sh.setFormatter(colorlog.ColoredFormatter(fmt))

    return sh


def __main__(argv=sys.argv):
    if len(argv) < 2:
        print(
            "usage: <class> [method [method-args]] [--logging name-level-args] [--output DIR] [--search-path DIR] [--config config-args]"
        )
        sys.exit(1)

    args = parse_args(
        argv[1:],
        bool_options=["--rm", "--get-path", "--log-artifacts"],
        val_options=["--logging", "--output", "--search-path", "--wandb"],
    )

    if "--logging" in args["options"]:
        log_setup = {}
        for name, orig_level in config_list_to_dict(args["options"]["--logging"].split(",")).items():
            level = "WARNING" if orig_level.upper() == "WARN" else orig_level
            level = logging.getLevelName(level.upper())
            if isinstance(level, str):
                raise RuntimeError(f"invalid level with logger name={name}: {orig_level}")

            _logger = logging.getLogger(name)
            _logger.setLevel(level)
            _logger.addHandler(log_handler())
            _logger.propagate = False  # turn off propagate when we're handling the message
            log_setup[name] = logging._levelToName[level]
        logger.debug("configured loggers: %s", log_setup)

    logger.debug("parsed arguments: %s", args)

    config = config_list_to_dict(args["cls_config"])
    config["_cls"] = args["cls"]
    cmd = args["cmd"] if args["cmd"] else "main"
    cmd_args = config_list_to_dict(args["cmd_args"])

    output_path = args["options"].get("--output", "/doesnt/exist")
    search_path = args["options"]["--search-path"].split(":") if "--search-path" in args["options"] else []
    if output_path not in search_path:
        search_path.append(output_path)

    obj = instantiate_object(
        config,
        search_path=search_path,
        output_path=output_path,
    )

    # cmd is an ingredient path followed by a method, like index.collection.somemethod
    # find the method and replace obj with the index.collection
    cmd_parts = cmd.split(".")
    methodstr = cmd_parts.pop()
    for ingredient in cmd_parts:
        # TODO handle indexing into list more generally
        if isinstance(obj, list):
            obj = obj[0]
        obj = obj.cfg[ingredient]

    # TODO this is broken with cached_property, because the method runs when we attempt to get it and build() is not yet run
    method = getattr(obj, methodstr)

    if "--log-artifacts" in args["options"]:
        Ingredient.artifact_log = []

    if "from_pkl" in cmd_args:
        with open(cmd_args["from_pkl"], "rb") as f:
            cmd_args = pickle.load(f)
    else:
        _, invalid_args, default_args = parse_function_arguments(method, args=[], kwargs=cmd_args)
        if invalid_args:
            raise RuntimeError(
                f"invalid arguments for method command {methodstr}: {invalid_args.keys()}"
                + f"\n\tThis method's default arguments are: {default_args}"
            )

        cmd_args = cast_dict_to_types(cmd_args, getattr(method, "__annotations__", {}))

    # handle --rm by removing the cached output, if it exists
    if "--rm" in args["options"]:
        obj.build()
        try:
            output = method(_read_only=True, _output_tuple=True, **cmd_args)
        except ReadOnlyException:
            output = None

        if output:
            output.rm()
            print("removed:", output.path)
        return

    # need a tuple so we can read the path later
    if "--get-path" in args["options"]:
        cmd_args["_output_tuple"] = True

    if "--wandb" in args["options"]:
        import wandb

        wandb.init(project=args["options"]["--wandb"], config=obj.dict_config())

        # log the original dict_config
        outfn = os.path.join(wandb.run.dir, "dict_config.json")
        with open(outfn, "wt", encoding="utf-8") as outf:
            json.dump(obj.dict_config(), outf, indent=4, sort_keys=True)
        wandb.save(outfn)

    if hasattr(obj, "build"):
        obj.build()
    output = method(**cmd_args)

    if "--wandb" in args["options"]:
        wandb.finish()

    if "--get-path" in args["options"]:
        print("path:", output.path)

    if "--log-artifacts" in args["options"]:
        print("-------------- artifact log records ----------------")
        for entry in obj.artifact_log:
            print(
                f"cache={entry.output.from_cache} duration={entry.end_time-entry.start_time}"
                + f"\tstart={entry.start_time}\tend={entry.end_time}"
            )
            print("\t" + " ".join(entry.cmd))
        # with open("artlogs.pkl", "wb") as outf:
        #     pickle.dump(log, outf)

    print("\ncommand output:", output)
    return output

    # consider:
    # --cp: copy the final output object to the given path (this might be empty...)
    # output.cp(dest)
    # --mv: move the final output object to the given path (this might be empty...)
    # output.mv(dest)
    # a 'cls' version of the above, like --cls-cp and --cls-rm, that operate on all artifacts for the cls (with the current cfg)
    #                                 or --cp-cls


if __name__ == "__main__":
    __main__()
