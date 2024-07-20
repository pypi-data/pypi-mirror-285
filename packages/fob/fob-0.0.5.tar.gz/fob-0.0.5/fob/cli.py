import collections.abc
import os
from collections import OrderedDict
from shlex import shlex


def parse_args(args, config_switch="--config", bool_options=["--rm"], val_options=["--output", "--search-path"]):
    before_config = []
    in_config = []
    in_option = None
    options = OrderedDict()
    found_config = False
    for arg in args:
        if arg == config_switch:
            found_config = True
            continue

        if in_option and (arg in bool_options or arg in val_options):
            # we were inside an option, but we encountered another flag (e.g. "--wandb")
            # rather than a value, so we set the value to None
            options[in_option] = None
            in_option = None

        if in_option:
            options[in_option] = arg
            in_option = None
        elif arg.startswith("--"):
            if arg in val_options:
                in_option = arg
            elif arg in bool_options:
                pass
            else:
                raise ValueError("unknown option %s" % arg)
            options[arg] = ""
        elif found_config:
            in_config.append(arg)
        else:
            before_config.append(arg)

    cls, cmd = None, None
    cmd_args = []
    if len(before_config) > 0:
        cls = before_config.pop(0)
    if len(before_config) > 0:
        next_arg = before_config.pop(0)
        if "=" in next_arg:
            cmd_args.append(next_arg)
        else:
            cmd = next_arg
    cmd_args = cmd_args + before_config

    return {"options": options, "cls": cls, "cmd": cmd, "cmd_args": cmd_args, "cls_config": in_config}


######


def config_dict_to_string(d, prefix=""):
    l = []
    for k, v in d.items():
        if isinstance(v, dict):
            l.append(config_dict_to_string(v, prefix=f"{prefix}{k}."))
        else:
            l.append(f"{prefix}{k}={v}")

    return " ".join(l)


def config_string_to_dict(s):
    s = " ".join(s.split())  # remove consecutive whitespace
    return config_list_to_dict(s.split())


def config_list_to_dict(l):
    d = {}

    for k, v in _config_list_to_pairs(l):
        _dot_to_dict(d, k, v)

    return d


def _dot_to_dict(d, k, v):
    if k.startswith(".") or k.endswith("."):
        raise ValueError(f"invalid path: {k}")

    if "." in k:
        path = k.split(".")
        current_k = path[0]
        remaining_path = ".".join(path[1:])

        # this is a list of objects, which uses the key.name,= syntax to start a new list item
        if remaining_path.endswith(",") and "." not in remaining_path:
            # if d[current_k] is already a dict (eg from an earlier config option we're now overriding), delete it
            if isinstance(d.get(current_k), dict):
                # logger.warning("replacing %s=%s with an empty list", k, d[current_k])
                del d[current_k]

            # add a new dict to to the list of objects, which we will switch to and populate below
            d.setdefault(current_k, []).append({})

            # removing the trailing , so that the key in d looks normal when we populate it below
            remaining_path = remaining_path[:-1]

        # if current_k is a list, populate the last d in the list
        if isinstance(d.get(current_k), list):
            _dot_to_dict(d[current_k][-1], remaining_path, v)
        # otherwise, treat it as a dict as normal
        else:
            d.setdefault(current_k, {})
            _dot_to_dict(d[current_k], remaining_path, v)
    else:
        d[k] = v


def _config_list_to_pairs(l, prefix=""):
    pairs = []
    for kv in l:
        kv = kv.strip()

        if len(kv) == 0:
            continue

        if kv.count("=") != 1:
            raise ValueError(f"invalid 'key=value' pair: {kv}")

        k, v = kv.split("=")
        if len(v) == 0:
            raise ValueError(f"invalid 'key=value' pair: {kv}")

        k = prefix + k

        if k.lower() == "file" or k.lower().endswith(".file"):
            parent_k = k[:-4]  # remove "file" from the end
            pairs.extend(_config_list_to_pairs(_config_file_to_list(v), prefix=parent_k))
        elif k.lower() == "file," or k.lower().endswith(".file,"):
            parent_k = k[:-5]  # remove "file," from the end
            # add the , back to the first key to replace the , removed from file
            tmp = _config_list_to_pairs(_config_file_to_list(v), prefix=parent_k)
            if len(tmp) > 0:
                tmp[0] = (tmp[0][0] + ",", tmp[0][1])
            pairs.extend(tmp)
        else:
            pairs.append((k, v))

    return pairs


def _config_file_to_list(fn):
    lst = []
    with open(os.path.expanduser(fn), "rt") as f:
        for line in f:
            lex = shlex(line)
            lex.whitespace = ""
            kvs = "".join(list(lex))
            for kv in kvs.strip().split():
                lst.append(kv)

    return lst


# merge two dicts recursively (handling nested dicts): https://stackoverflow.com/a/3233356
def update_dict(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d
