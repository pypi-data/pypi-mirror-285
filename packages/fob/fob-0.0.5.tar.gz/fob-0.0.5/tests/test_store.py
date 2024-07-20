import os
import pickle

import numpy as np
import pytest

from typing import Type

from fob.base import instantiate_object
from fob.cli import config_string_to_dict
from fob.ingredient import configurable, Ingredient
from fob.serialize import NumpyOutput, PathOutput
from fob.store import cacheable, ReadOnlyException, store_method_args, FunctionOutput


@pytest.fixture
def noconfig_class():
    class Test:
        def cache_str(self):
            return "/stuff/Test"

        @cacheable(NumpyOutput)
        def some_calculation(self, x, y, _output_tuple=True):
            data = np.array([0, x, y, x + y])
            return data

        @cacheable(PathOutput)
        def some_file_creation(self, stuff, tmp_path_context=None, _output_tuple=True):
            with tmp_path_context() as path:
                with open(path, "wt") as outf:
                    print(stuff, file=outf)
                return path

        @cacheable(PathOutput)
        def some_dir_creation(self, stuff, tmp_path_context=None, _output_tuple=True):
            with tmp_path_context() as path:
                os.makedirs(path)
                for fn in range(3):
                    fn = "index-file-" + str(fn)
                    with open(os.path.join(path, fn), "wt") as outf:
                        print(stuff, fn, file=outf)
                return path

        @cacheable(NumpyOutput)
        def some_array(self, lst, foo=None, _output_tuple=True):
            return np.array(lst)

    return Test


def test_function_only(tmp_path):
    def some_func(a, _output_path=tmp_path, _search_path=[tmp_path]):
        return a**3

    cacheable_func = cacheable(NumpyOutput)(some_func)
    assert some_func(3) == cacheable_func(3)
    assert cacheable_func(3, _output_tuple=True).from_cache
    assert cacheable_func(3, _output_tuple=True, _output_path=None).from_cache
    assert not cacheable_func(3, _output_tuple=True, _search_path=None).from_cache


def test_function_skip(tmp_path):
    def some_func(a, b, _output_path=tmp_path, _search_path=[tmp_path]):
        return a**3

    cacheable_func = cacheable(NumpyOutput, skip=["b"])(some_func)
    cacheable_func(3, 123)
    assert cacheable_func(3, 456, _output_tuple=True).from_cache
    assert not cacheable_func(4, 456, _output_tuple=True, _search_path=None).from_cache


def test_basic(noconfig_class, tmp_path):
    t = noconfig_class()
    t.output_path = tmp_path
    t.search_path = [tmp_path]

    assert not t.some_calculation(1, 3).from_cache
    assert t.some_calculation(1, 3).from_cache

    assert not t.some_calculation(1, 3, _version="impossible").from_cache
    assert not t.some_calculation(1, 3, _version="missagain").from_cache
    assert t.some_calculation(1, 3, _version="impossible").from_cache

    t._version = "anothermiss"
    assert not t.some_calculation(1, 3).from_cache
    assert t.some_calculation(1, 3, _version="impossible").from_cache

    assert not t.some_calculation(3, 3).from_cache
    assert not t.some_calculation(3, 1).from_cache
    assert not t.some_calculation(1, 1).from_cache

    assert not t.some_array([1, 2, 3]).from_cache
    assert t.some_array([1, 2, 3]).from_cache

    assert not t.some_array([1, 2, 3], foo="bar").from_cache
    assert not t.some_array([1, 2, 3], foo="foo").from_cache
    assert t.some_array([1, 2, 3], foo="foo").from_cache

    assert not t.some_file_creation("a thing").from_cache
    assert not t.some_file_creation(123).from_cache
    assert t.some_file_creation("a thing").from_cache

    assert not t.some_dir_creation("a thing").from_cache
    assert not t.some_dir_creation(123).from_cache
    assert t.some_dir_creation("a thing").from_cache


def test_output_tuple_override(noconfig_class, tmp_path):
    t = noconfig_class()
    t.output_path = tmp_path
    t.search_path = [tmp_path]

    assert hasattr(t.some_calculation(1, 1, _output_tuple=True), "from_cache")
    assert not hasattr(t.some_calculation(1, 1, _output_tuple=False), "from_cache")


def test_output_and_search_path_overrides(noconfig_class, tmp_path):
    output_path1 = tmp_path / "1"
    output_path2 = tmp_path / "2"

    t = noconfig_class()
    t.output_path = output_path1
    t.search_path = [output_path1]

    t.some_calculation(9, 9, _output_path=output_path2)
    assert not t.some_calculation(9, 9).from_cache
    assert not t.some_calculation(9, 9, _search_path=[]).from_cache
    assert t.some_calculation(9, 9, _search_path=[output_path2]).from_cache
    assert t.some_calculation(9, 9, _search_path=[output_path1]).from_cache

    t.output_path = None
    t.search_path = []
    assert not t.some_calculation(9, 9, _output_path=None, _search_path=[]).from_cache
    assert not t.some_calculation(9, 9, _output_path=None, _search_path=[]).from_cache


def test_fail_on_missing(noconfig_class, tmp_path):
    t = noconfig_class()
    t.output_path = tmp_path
    t.search_path = [tmp_path]

    with pytest.raises(ReadOnlyException):
        t.some_calculation(1, 1, _read_only=True)

    t.read_only = True
    with pytest.raises(ReadOnlyException):
        t.some_calculation(1, 1)

    t.some_calculation(1, 1, _read_only=False)
    t.some_calculation(1, 1, _read_only=True)


def test_artifact_log(noconfig_class, tmp_path):
    class TestIngredient(Ingredient, noconfig_class):
        @configurable
        def __init__(self, child: Type[Ingredient] = None):
            pass

    t = TestIngredient(child=TestIngredient())
    t.set_paths(output_path=str(tmp_path), search_path=[str(tmp_path)])

    Ingredient.artifact_log = []
    assert isinstance(t.artifact_log, list)
    assert len(t.artifact_log) == 0

    t.some_calculation(1, 2)
    assert len(t.artifact_log) == 1
    assert t.artifact_log[-1].output.from_cache == False

    t.some_calculation(1, 2)
    assert len(t.artifact_log) == 2
    assert t.artifact_log[-1].output.from_cache == True

    assert t.artifact_log[-1].cmd == t.artifact_log[-2].cmd

    t.cfg["child"].some_calculation(1, 2)
    assert len(t.artifact_log) == 3
    assert t.cfg["child"].artifact_log[-1].output.from_cache == False

    Ingredient.artifact_log = None


def test_store_cfg_file(tmp_path):
    cfg = {
        "_cls": "widget.WidgetPair",
        "widget1": {"_cls": "widget.RoundWidget", "radius": 2},
        "widget2": {"_cls": "widget.RoundWidget", "radius": 3.0},
    }
    pair = instantiate_object(cfg, output_path=tmp_path, search_path=[tmp_path])
    pair.cfg_file()

    out = pair.cfg_file(_read_only=True, _output_tuple=True)
    paircp = instantiate_object(config_string_to_dict("file=" + os.path.join(out.path, "out.txt")))
    assert pair.cache_str() == paircp.cache_str()

    pairdiff = instantiate_object(config_string_to_dict("file=" + os.path.join(out.path, "out.txt") + " widget1.radius=4"))
    assert pair.cache_str() != pairdiff.cache_str()


def test_store_method_args(tmp_path):
    kwargs = {"foo": 1, "bar": "test"}
    store_method_args(kwargs, _output_path=tmp_path, _search_path=[tmp_path])
    store_method_args(kwargs, _output_path=tmp_path, _search_path=[tmp_path], _read_only=True)

    out = store_method_args(kwargs, _output_path=tmp_path, _search_path=[tmp_path, "empty"], _read_only=True, _output_tuple=True)
    assert pickle.load(open(os.path.join(out.path, "out.pkl"), "rb")) == kwargs

    kwargs2 = {"foo": 1}
    out2 = store_method_args(kwargs2, _output_path=tmp_path, _search_path=[tmp_path], _output_tuple=True)
    assert pickle.load(open(os.path.join(out2.path, "out.pkl"), "rb")) != kwargs
    assert pickle.load(open(os.path.join(out2.path, "out.pkl"), "rb")) == kwargs2


def test_functionoutput_file_ops(tmp_path):
    path1 = str(tmp_path / "1")
    os.makedirs(path1, exist_ok=True)
    fo = FunctionOutput(output=None, from_cache=False, cache_key="KEY", path=str(tmp_path / "1"))
    assert os.path.exists(path1)
    fo.rm()
    assert not os.path.exists(path1)
    assert os.path.exists(tmp_path)

    path2 = str(tmp_path / "2")
    os.makedirs(path1, exist_ok=True)
    fo.cp(path2)
    assert os.path.exists(os.path.join(path2, "KEY"))

    path3 = str(tmp_path / "3")
    assert os.path.exists(path1)
    fo.mv(path3)
    assert not os.path.exists(path1)
    assert os.path.exists(os.path.join(path3, "KEY"))
