import contextlib
import json
import logging
import os
import pickle
import shutil
from pathlib import Path

import numpy as np
from trecrun import TRECRun


logger = logging.getLogger(__name__)
# do not seed, because RNG's purpose is to avoid filename conflicts
_pathrng = np.random.default_rng()


class TemporaryOutputPath(object):
    def __init__(self, base_path, cleanup_on_exception=True, mkdir=False):
        self.cleanup_on_exception = cleanup_on_exception
        self.mkdir = mkdir
        self.base_path = base_path
        self.path = None

    def __enter__(self):
        while self.path is None or os.path.exists(self.path):
            self.path = Path(os.path.join(self.base_path, f"tmp_{os.getpid()}_{_pathrng.random()}"))

        if self.mkdir:
            os.makedirs(self.path, exist_ok=False)

        return self.path

    def __exit__(self, extype, value, traceback):
        if extype is not None and self.cleanup_on_exception:
            # remove temporary path if an error is thrown
            shutil.rmtree(self.path)
            return


class AtomicOutputPath(object):
    def __init__(self, final_path, tmp_base_path, cleanup_on_exception=True):
        self.tmp_output_context = TemporaryOutputPath(tmp_base_path, cleanup_on_exception=cleanup_on_exception, mkdir=True)
        self.final_path = final_path
        self.tmp_base_path = tmp_base_path

    def __enter__(self):
        with contextlib.ExitStack() as stack:
            self.tmp_path = stack.enter_context(self.tmp_output_context)
            self._stack = stack.pop_all()
        return self.tmp_path

    def __exit__(self, extype, value, traceback):
        if extype is None:
            # move to the final path if an exception is not being raised
            shutil.move(self.tmp_path, self.final_path)
            # TODO does empty check make sense here? will config.json exist??
            # remove the tmp directory if it's empty
            if os.path.exists(self.tmp_base_path) and len(os.listdir(self.tmp_base_path)) == 0:
                shutil.rmtree(self.tmp_base_path)

        self._stack.__exit__(extype, value, traceback)


class CacheableOutput:
    always_reload = False

    @classmethod
    def exists_in(cls, path):
        full_path = os.path.join(path, cls.format)
        return os.path.exists(full_path)


class PathOutput(CacheableOutput):
    """Used with functions that return a path."""

    format = "out"
    always_reload = True

    @classmethod
    def serialize(cls, obj, output_dir):
        output_path = os.path.join(output_dir, cls.format)
        assert not os.path.exists(output_path)

        tmp_path = obj
        shutil.move(tmp_path, output_path)
        return output_path

    @classmethod
    def deserialize(cls, input_dir):
        fn = os.path.join(input_dir, cls.format)
        return fn


class NumpyOutput(CacheableOutput):
    """Used with functions that return a numpy array."""

    format = "out.npy"  # needs to end in .npy to prevent numpy from adding this
    # TODO add a mmap_mode to init (for r, c, r+, w+)

    @classmethod
    def serialize(cls, obj, output_dir):
        output_fn = os.path.join(output_dir, cls.format)
        np.save(output_fn, obj, allow_pickle=False, fix_imports=False)
        return obj

    @classmethod
    def deserialize(cls, input_dir):
        fn = os.path.join(input_dir, cls.format)
        return np.load(fn, mmap_mode="r", allow_pickle=False, fix_imports=False)


class DictNumpyOutput(CacheableOutput):
    """Used with functions that return a dict of numpy arrays."""

    format = "out.npz"  # needs to end in .npz to prevent numpy from adding this

    @classmethod
    def serialize(cls, obj, output_dir):
        output_fn = os.path.join(output_dir, cls.format)
        # obj should be a dict
        np.savez(output_fn, **obj)
        return obj

    @classmethod
    def deserialize(cls, input_dir):
        fn = os.path.join(input_dir, cls.format)
        # TODO can we avoid allow_pickle=True? or at least move to an argument?
        return np.load(fn, mmap_mode="r", allow_pickle=True, fix_imports=False)


class JsonOutput(CacheableOutput):
    format = "out.json"

    @classmethod
    def serialize(cls, obj, output_dir):
        output_fn = os.path.join(output_dir, cls.format)
        with open(output_fn, "wt", encoding="utf-8") as outf:
            json.dump(obj, outf)
        return obj

    @classmethod
    def deserialize(cls, input_dir):
        fn = os.path.join(input_dir, cls.format)
        with open(fn, "rt", encoding="utf-8") as f:
            return json.load(f)


class TRECRunOutput(CacheableOutput):
    """Used with TRECRun"""

    format = "run.txt"

    @classmethod
    def serialize(cls, obj, output_dir):
        output_fn = os.path.join(output_dir, cls.format)
        obj.write_trec_run(output_fn, tag="run")
        return obj

    @classmethod
    def deserialize(cls, input_dir):
        fn = os.path.join(input_dir, cls.format)
        return TRECRun(fn)


class PickleOutput(CacheableOutput):
    format = "out.pkl"

    @classmethod
    def serialize(cls, obj, output_dir):
        output_fn = os.path.join(output_dir, cls.format)
        with open(output_fn, "wb") as outf:
            pickle.dump(obj, outf)
        return obj

    @classmethod
    def deserialize(cls, input_dir):
        fn = os.path.join(input_dir, cls.format)
        with open(fn, "rb") as f:
            return pickle.load(f)


class StringOutput(CacheableOutput):
    format = "out.txt"

    @classmethod
    def serialize(cls, obj, output_dir):
        output_fn = os.path.join(output_dir, cls.format)
        with open(output_fn, "wt", encoding="utf-8") as outf:
            print(obj, file=outf)
        return obj

    @classmethod
    def deserialize(cls, input_dir):
        fn = os.path.join(input_dir, cls.format)
        with open(fn, "rt", encoding="utf-8") as f:
            return f.read().rstrip()


# LTODO changing output type of an existing cached function will break the final directory mv, because the target dir already exists, resulting in the tmp path moving to targetdir/subdir rather than becoming targetdir
