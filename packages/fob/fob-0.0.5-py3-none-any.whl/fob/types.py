import logging
import typing

import numpy as np
from trecrun import TRECRun


logger = logging.getLogger(__name__)

primitive_config_types = {str, float, int, bool, None}

valid_config_types = set()
for base_type in primitive_config_types:
    valid_config_types.add(base_type)
    valid_config_types.add(typing.List[base_type])
    valid_config_types.add(typing.Union[base_type, typing.List[base_type]])

annotation_to_typef = {
    float: lambda x: None if str(x) == "None" else float(x),
    int: lambda x: None if str(x) == "None" else int(x),
    str: lambda x: None if str(x) == "None" else str(x),
    None: lambda x: None if str(x) == "None" else x,
    bool: lambda x: str(x).lower() not in ("false", "none"),
}


convertable_types = {TRECRun: TRECRun}


def cast_dict_to_types(d, annotations):
    from fob.ingredient import Ingredient

    castd = d.copy()
    for k, v in d.items():
        arg_type = annotations.get(k, "missing")
        if arg_type in valid_config_types:
            castd[k] = cast_string_to_type(v, arg_type)
        elif v == "None":
            castd[k] = None
        else:
            type_annotation = simple_type_annotation_to_type(arg_type)[2] if arg_type != "missing" else str
            if k == "_cls":
                pass
            elif type_annotation in convertable_types:
                logger.debug(f"converting type of {k}: {convertable_types[type_annotation]}")
                castd[k] = convertable_types[type_annotation](k)
            elif not issubclass(type_annotation, Ingredient):
                logger.warning("type_annotation=%s for %s not in valid_config_types", arg_type, k)

    return castd


def simple_type_annotation_to_type(type_annotation):
    list_type_found = False

    if type_annotation in primitive_config_types:
        return list_type_found, annotation_to_typef.get(type_annotation, type_annotation), type_annotation

    # return a no-op annotation if nothing matches
    if not hasattr(type_annotation, "__args__"):
        return list_type_found, lambda x: x, type_annotation

    # 'simple' means we only allow one type (eg float union float list), so stop as soon as we find any basic type
    for sub_type in type_annotation.__args__:
        if type(sub_type) == typing._GenericAlias:
            list_type_found = True
            type_function = sub_type.__args__[0]
            break
        else:
            type_function = sub_type
            list_type_found = type(type_annotation) == typing._GenericAlias
            # can't break in case we would later set list_type_found=True

    return list_type_found, annotation_to_typef.get(type_function, type_function), type_function


def cast_string_to_type(s, type_annotation):
    if type_annotation not in valid_config_types:
        logger.warning("type_annotation=%s not in valid_config_types", type_annotation)

    list_type_found, type_function, _ = simple_type_annotation_to_type(type_annotation)

    if list_type_found:
        return convert_string_to_list(s, type_function)
    else:
        return type_function(s)


def convert_string_to_list(values, item_type):
    """Convert a comma-seperated string '1,2,3' to a list of item_type elements. Does nothing if values is not a str.
    Supports ranges with the syntax 'start..stop,step', which are expanded to include both endpoints."""
    if not isinstance(values, str):
        return values

    as_range = _parse_string_as_range(values, item_type)
    if as_range:
        return as_range

    return [item_type(x) for x in values.split(",")]


def _parse_string_as_range(s, item_type):
    """Try to parse s as 'start..stop,step' and expand it to a range including both endpoints."""
    if item_type not in (float, int):
        return None

    parts = s.split(",")
    if len(parts) != 2:
        return None

    ends = parts[0].split("..")
    if len(ends) != 2:
        return None

    start, stop = ends
    start, stop = item_type(start), item_type(stop)
    step = item_type(parts[1])

    if stop <= start:
        raise ValueError(f"invalid range: {s}")

    if item_type == int:  # noqa: E721
        return list(range(start, stop + step, step))
    elif item_type == float:  # noqa: E721
        precision = max(_rounding_precision(x) for x in (start, stop, step))
        lst = [round(item, precision) for item in np.arange(start, stop + step, step)]
        if lst[-1] > stop:
            del lst[-1]
        return lst


def _rounding_precision(x):
    x = str(x)
    if len(x.split(".")) == 2:
        return len(x.split(".")[1])
    elif len(x.split("e-")) == 2:
        return int(x.split("e-")[1])
    else:
        raise ValueError(f"cannot parse: {x}")


def cfg_as_strings(cfg, prefix=""):
    prefix = prefix + "." if prefix else ""

    primitives, deps = [], []
    for k, v in sorted(cfg.items()):
        if hasattr(v, "cfg"):
            deps.append((k, v))
        else:
            primitives.append((k, v))

    for k, v in primitives:
        if isinstance(v, list):
            v = ",".join([str(x) for x in v])
        yield f"{prefix}{k}={v}"

    for k, v in deps:
        yield from cfg_as_strings(v.cfg, prefix + k)
