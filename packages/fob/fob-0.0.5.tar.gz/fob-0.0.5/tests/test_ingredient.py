import pytest

from typing import Type

from fob.ingredient import Ingredient, configurable
from fob.base import instantiate_object
from fob.store import cacheable
from fob.serialize import NumpyOutput

from widget import WidgetPair


def test_build_and_warm_run():
    global build_count
    build_count = 0
    global warm_count
    warm_count = 0

    class SomeIngredient(Ingredient):
        def build(self):
            super().build()
            global build_count
            build_count += 1

        def warm(self):
            super().warm()
            global warm_count
            warm_count += 1

        @configurable
        def __init__(self, a: Type[Ingredient] = None, b: Type[Ingredient] = None):
            pass

    some = SomeIngredient()
    some.build()
    assert build_count == 1
    some.warm()
    assert warm_count == 1

    more = SomeIngredient(a=SomeIngredient(), b=SomeIngredient(a=SomeIngredient()))
    print(more.dict_config())
    more.build()
    assert build_count == 5
    more.warm()
    assert warm_count == 5


def test_ingredient_from_path(tmp_path):
    orig_area = WidgetPair.area
    WidgetPair.area = cacheable(NumpyOutput)(WidgetPair.area)

    cfg = {
        "_cls": "widget.WidgetPair",
        "widget1": {"_cls": "widget.RoundWidget", "radius": 12},
        "widget2": {"_cls": "widget.RoundWidget", "radius": 11.0},
    }
    pair = instantiate_object(cfg, output_path=str(tmp_path), search_path=[str(tmp_path)])
    out = pair.area(100, _output_tuple=True)

    paircp = Ingredient.from_path(out.path + "/../", append_search_path=["/testappend"])
    assert paircp.search_path[-1] == "/testappend"
    assert paircp.dict_config() == pair.dict_config()
    assert paircp.cache_str() == pair.cache_str()
    WidgetPair.area = orig_area  # probably a terrible idea


def test_caching_like():
    from widget import RoundWidget

    a = WidgetPair(RoundWidget(1), RoundWidget(2))
    assert a.search_path is None
    assert a.output_path is None
    assert a.cfg["widget1"].search_path is None
    assert a.cfg["widget1"].output_path is None
    assert a.cfg["widget2"].search_path is None
    assert a.cfg["widget2"].output_path is None

    path1 = "/something"
    path2 = "/other"
    a.cfg["widget1"].search_path = [path1]
    a.cfg["widget1"].output_path = path1

    a.set_paths(search_path=[path2], output_path=path2, recurse=False, overwrite_existing=False)
    assert a.search_path == [path2]
    assert a.output_path == path2
    assert a.cfg["widget1"].search_path == [path1]
    assert a.cfg["widget1"].output_path == path1
    assert a.cfg["widget2"].search_path is None
    assert a.cfg["widget2"].output_path is None

    a.set_paths(search_path=[path2], output_path=path2, recurse=True, overwrite_existing=False)
    assert a.search_path == [path2]
    assert a.output_path == path2
    assert a.cfg["widget1"].search_path == [path1]
    assert a.cfg["widget1"].output_path == path1
    assert a.cfg["widget2"].search_path == [path2]
    assert a.cfg["widget2"].output_path == path2

    a.caching_like(a)
    assert a.search_path == [path2]
    assert a.output_path == path2
    assert a.cfg["widget1"].search_path == [path2]
    assert a.cfg["widget1"].output_path == path2
    assert a.cfg["widget2"].search_path == [path2]
    assert a.cfg["widget2"].output_path == path2


def test_configurable_raises_noninit_error():
    class Broken(Ingredient):
        @configurable
        def __init__(self):
            pass

        @configurable
        def incorrect_usage(self):
            pass

    b = Broken()
    with pytest.raises(AssertionError):
        b.incorrect_usage()
