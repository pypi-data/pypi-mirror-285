import datetime
import functools
import hashlib
import inspect
import json
import logging
import os
import shutil
import subprocess

from .serialize import AtomicOutputPath, PickleOutput, TemporaryOutputPath


class FunctionOutput:
    __slots__ = ("output", "from_cache", "cache_key", "path")

    def __init__(self, output, from_cache, cache_key, path):
        self.output = output
        self.from_cache = from_cache
        self.cache_key = cache_key
        self.path = path

    def rm(self):
        # prevent access while rmtree is running by moving the directory to a tmp path
        tmp_path = self.path + ".tmp"
        shutil.move(self.path, tmp_path)
        shutil.rmtree(tmp_path)

    def cp(self, dest):
        dest = os.path.join(dest, self.cache_key)
        shutil.copytree(self.path, dest)

    def mv(self, dest):
        self.cp(dest)
        self.rm()


class ArtifactLogRecord:
    def __init__(self, start_time=None, end_time=None, output=None, cmd=None):
        self.start_time = start_time
        self.end_time = end_time
        self.output = output
        self.cmd = cmd

    def __str__(self):
        return (
            f"ArtifactLogRecord<<{self.end_time - self.start_time} - {self.start_time} - {self.end_time} - "
            + f"cache: {self.output.from_cache} - cmd: {self.cmd}>>"
        )


# Function arguments that should be ignored when checking the cache, such as input/output paths
_function_cache_path_skip = {"_output_tuple", "_output_path", "_search_path", "_read_only", "_exec", "tmp_path_context"}
# Function arguments (e.g., for modifying caching behavior) that should be dropped before calling the decorated function
_function_kwargs_drop = {"_output_tuple", "_output_path", "_search_path", "_read_only", "_exec", "_version"}

logger = logging.getLogger(__name__)


class ReadOnlyException(Exception):
    pass


def find_output_path(search_path, output_type, cache_hash):
    if search_path:
        for path in [os.path.join(x, cache_hash) for x in search_path]:
            if output_type.exists_in(path):
                return path
    return None


def get_output_path(output_path, cache_hash):
    if not output_path:
        logger.critical("output_path is not set")
    return os.path.join(output_path, cache_hash)


def get_tmp_path(output_path, cache_hash):
    if not output_path:
        logger.critical("output_path is not set")
    return os.path.join(output_path, "tmp", cache_hash)


def tmp_path_contextf(output_path, cache_hash):
    tmp_base_dir = get_tmp_path(output_path, cache_hash)
    os.makedirs(tmp_base_dir, exist_ok=True)
    context_func = functools.partial(TemporaryOutputPath, tmp_base_dir)
    return context_func


def output_path_context(output_path, cache_hash):
    final_path = get_output_path(output_path, cache_hash)
    tmp_path = get_tmp_path(output_path, cache_hash)
    return AtomicOutputPath(final_path, tmp_path)


def function_cache_path(f, skip_params, version, *args, **kwargs):
    params, _, _ = parse_function_arguments(f, args, kwargs)

    assert "_func" not in params
    params["_func"] = f.__name__

    assert "_self" not in params
    self = params.get("self", None)
    if "self" in params:
        params["_self"] = params["self"].cache_str()
        del params["self"]
    else:
        params["_self"] = ""

    if not version and self is not None and hasattr(self, "_version"):
        version = getattr(self, "_version")
    params["_version"] = version

    hash_params = {
        k: v.cache_str() if hasattr(v, "cache_str") else v
        for k, v in params.items()
        if k not in _function_cache_path_skip and k not in skip_params
    }
    hash_string = json.dumps(hash_params, sort_keys=True)
    cache_hash = params["_func"] + "_" + hashlib.sha256(hash_string.encode("utf-8")).hexdigest()
    logger.debug("%s%s", self.__module__ + "." + self.__class__.__name__ + "." if self is not None else "", cache_hash)

    if self is not None:
        module_hash = (
            self.__module__ + "." + self.__class__.__name__ + "_" + hashlib.sha256(params["_self"].encode("utf-8")).hexdigest()
        )
    else:
        module_hash = "function"

    return hash_params, hash_string, module_hash, cache_hash, self


def parse_function_arguments(func, args, kwargs):
    sig = inspect.signature(func)
    valid_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
    invalid_args = {k: v for k, v in kwargs.items() if k not in valid_kwargs}

    default_args = {k: v.default for k, v in sig.parameters.items()}
    bound_args = sig.bind(*args, **valid_kwargs).arguments
    bound_args = {k: bound_args.get(k, v) for k, v in default_args.items()}

    return bound_args, invalid_args, default_args


def cacheable(output_type, skip=[]):
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            all_args, _, _ = parse_function_arguments(func, args, kwargs)
            all_args.update(kwargs)  # add back stuff like _output_path that may not appear in function signature

            cache_params, cache_string, module_hash, func_hash, self = function_cache_path(
                func, skip, all_args.get("_version"), *args, **kwargs
            )
            cache_hash = os.path.join(module_hash, func_hash)

            output_tuple = bool(all_args.get("_output_tuple"))
            pyexec = all_args.get("_exec", None)

            output_path = all_args.get("_output_path")
            if output_path is None and self is not None and hasattr(self, "output_path"):
                output_path = self.output_path

            search_path = all_args.get("_search_path")
            if search_path is None and self is not None and hasattr(self, "search_path"):
                search_path = self.search_path

            read_only = all_args.get("_read_only")
            if read_only is None and self is not None and hasattr(self, "read_only"):
                read_only = self.read_only

            logrecord = None
            if hasattr(self, "artifact_log") and self.artifact_log is not None:
                if func.__name__ != "cfg_file":  # avoid recursive calls
                    logrecord = ArtifactLogRecord(start_time=datetime.datetime.now())
                    logrecord.cmd = generate_fob_command(
                        cls=self.__module__ + "." + self.__class__.__name__,
                        func=func.__name__,
                        kwargs={k: v for k, v in all_args.items() if k != "self"},
                        output_path=output_path,
                        search_path=search_path,
                        cfg_file_tuple=self.cfg_file(_output_path=output_path, _output_tuple=True),
                    )
                    self.artifact_log.append(logrecord)

            object_path = find_output_path(search_path, output_type, cache_hash) if search_path else None

            # there are four possible cases, in order:
            # (1) we found the object in the cache, so we load the object to return directly
            #
            # or we did not find the object in the cache, and ...
            #   (2) read_only is set, so we throw an exception
            #   (3) pyexec is set, so we create the object using the pyexec script (and then load and return it)
            #   (4) no special condition is set, so we create the object normally (and save it if output_path is set, and return it)
            if object_path:
                # load the cached output
                logger.debug("%s loading %s from path: %s", module_hash, output_type, object_path)
                from_cache = True
                data = output_type.deserialize(object_path)
            elif read_only:
                logger.debug(
                    "could not find %s with hash %s and read_only=True, so it will not be created", output_type, cache_hash
                )
                raise ReadOnlyException
            elif pyexec:
                # if _exec was set and object_path doesn't yet exist, we
                # (1) run the command with the _exec script to create object_path
                # (2) load the new object_path
                run_fob_command(
                    pyexec,
                    cls=self.__module__ + "." + self.__class__.__name__,
                    func=func.__name__,
                    kwargs={k: v for k, v in all_args.items() if k not in ("_exec", "self")},
                    output_path=output_path,
                    search_path=search_path,
                    cfg_file_tuple=self.cfg_file(_output_path=output_path, _output_tuple=True),
                )

                # now the cached output exists; load it as normal
                object_path = find_output_path(search_path, output_type, cache_hash) if search_path else None
                logger.debug("%s loading %s from path: %s", module_hash, output_type, object_path)
                from_cache = False
                data = output_type.deserialize(object_path)
            else:
                # run the function and (maybe) cache the result
                logger.debug("%s creating output to store in path: %s", module_hash, output_path)
                from_cache = False

                # assign if (1) the function has this kwarg and (2) it's still set to default None
                if "tmp_path_context" in (
                    inspect.getfullargspec(func).args + inspect.getfullargspec(func).kwonlyargs
                ) and not kwargs.get("tmp_path_context", None):
                    # TODO: rather than taking tmp_path_context as an argument, take the path to use as an argument.
                    # PathOutput can then work without specifying an output_path. This probably requires that fob enters the tmp_path context somewhere below?
                    kwargs["tmp_path_context"] = tmp_path_contextf(output_path, cache_hash)

                filtered_kwargs = {k: v for k, v in kwargs.items() if k not in _function_kwargs_drop}
                data = func(*args, **filtered_kwargs)

                if output_path:
                    if not os.path.exists(os.path.join(get_output_path(output_path, module_hash), "config.json")):
                        with output_path_context(output_path, module_hash) as module_data_path:
                            with open(os.path.join(module_data_path, "config.json"), "wt", encoding="utf-8") as outf:
                                print(cache_params.get("_self"), file=outf)

                    with output_path_context(output_path, cache_hash) as data_path:
                        with open(os.path.join(data_path, "params.json"), "wt", encoding="utf-8") as outf:
                            print(cache_string, file=outf)
                        data = output_type.serialize(data, data_path)

                    object_path = os.path.join(output_path, cache_hash)
                    logger.debug("%s created and serialized output %s", module_hash, cache_hash)

                    # if the output is a path, then it needs to be reloaded because output_path_context moves to a final path
                    if output_type.always_reload:
                        logger.debug("%s reloading %s", module_hash, output_type)
                        data = output_type.deserialize(object_path)
                else:
                    object_path = None
                    logger.debug("%s created but not serialized %s", module_hash, cache_hash)

            if logrecord:
                logrecord.end_time = datetime.datetime.now()
                logrecord.output = FunctionOutput(None, from_cache=from_cache, cache_key=cache_hash, path=object_path)
            return FunctionOutput(data, from_cache=from_cache, cache_key=cache_hash, path=object_path) if output_tuple else data

        return wrapper

    return inner


@cacheable(PickleOutput)
def store_method_args(kwargs: dict):
    return kwargs


def generate_fob_command(cls, func, kwargs, output_path, search_path, cfg_file_tuple):
    if len(kwargs) == 0:
        kwargstr = ""
    # the problem with outputing the args as text is that methods are not necessarily annotated, and
    # when a method isn't annotated, all its arguments become strings! for example, MAX_THREADS='8' becomes a new cache key...
    #
    # elif all(v is None or type(v) in primitive_config_types for v in kwargs.values()):
    #     string_kwargs = {k: str(v) for k, v in kwargs.items()}
    #     escaped = {k: f"'{v}'" if " " in v or "$" in v or "\\" in v else v for k, v in string_kwargs.items()}
    #     kwargstr = " ".join(f"{k}={v}" for k, v in escaped.items())
    else:
        kwarg_path = os.path.join(
            store_method_args(
                kwargs,
                _output_path=output_path,
                _output_tuple=True,
            ).path,
            "out.pkl",
        )

        kwargstr = "from_pkl=" + kwarg_path

    exec_args = (
        [cls, func]
        + kwargstr.split()
        + [
            "--output",
            output_path,
            "--search-path",
            ":".join(search_path),
            "--config",
            "file=" + os.path.join(cfg_file_tuple.path, "out.txt"),
        ]
    )

    return exec_args


def run_fob_command(pyexec, cls, func, kwargs, output_path, search_path, cfg_file_tuple):
    assert output_path
    assert search_path

    exec_args = generate_fob_command(cls, func, kwargs, output_path, search_path, cfg_file_tuple)
    exec_cmd = pyexec.split(" ") + exec_args
    logger.info("running subprocess: %s", " ".join(exec_cmd))
    with subprocess.Popen(exec_cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, text=True) as p:
        for line in p.stdout:
            print(line.rstrip())

        p.wait()
        if p.returncode != 0:
            raise RuntimeError("pyexec command failed: %s" % exec_cmd)

    return True
