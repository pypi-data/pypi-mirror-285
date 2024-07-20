import pickle

import pytest

from fob import configurable
from fob.base import instantiate_object, name_to_cls, __main__
from fob.store import cacheable
from fob.serialize import NumpyOutput

from widget import Widget, RoundWidget, WidgetPair


def test_name_to_cls():
    assert Widget == name_to_cls("widget.Widget")


def test_simple_instantiate_object_without_paths():
    obj = instantiate_object({"_cls": "widget.RoundWidget", "radius": 2.0})
    assert obj.cfg["radius"] == 2.0
    assert obj.area() == 2 * 3 * 2.0
    assert isinstance(obj, RoundWidget)
    assert (not hasattr(obj, "search_path")) or not obj.search_path
    assert (not hasattr(obj, "output_path")) or not obj.output_path


def test_simple_instantiate_object_with_paths():
    search_path = ["/some/path"]
    obj = instantiate_object({"_cls": "widget.RoundWidget", "radius": 2.0}, search_path=search_path, output_path="/output")
    assert obj.search_path == search_path
    assert obj.output_path == "/output"


def test_recursive_instantiate_object_without_paths():
    pair = instantiate_object(
        {"_cls": "widget.WidgetPair", "widget1": RoundWidget(2), "widget2": {"_cls": "widget.RoundWidget", "radius": 3}}
    )
    assert pair.area() == 2 * 3 * (2 + 3)


def test_recursive_instantiate_object_with_paths():
    search_path = ["/some/path"]
    pair = instantiate_object(
        {"_cls": "widget.WidgetPair", "widget1": RoundWidget(2), "widget2": {"_cls": "widget.RoundWidget", "radius": 3}},
        search_path=search_path,
        output_path="/output",
    )
    assert pair.search_path == search_path
    assert pair.output_path == "/output"
    # widget1 should have paths set because instantiate_object will call set_paths to replace empty ones
    assert pair.cfg["widget1"].search_path == search_path
    assert pair.cfg["widget1"].output_path == "/output"
    # widget2 should have paths set because it was created by instantiace_object
    assert pair.cfg["widget2"].search_path == search_path
    assert pair.cfg["widget2"].output_path == "/output"


def test_config_from_instantiate_object():
    pair = instantiate_object(
        {"_cls": "widget.WidgetPair", "widget1": RoundWidget(2), "widget2": {"_cls": "widget.RoundWidget", "radius": 3}},
    )
    assert pair.cfg["widget1"].cfg["radius"] == 2
    assert pair.cfg["widget2"].cfg["radius"] == 3

    # with default radius
    pair = instantiate_object(
        {"_cls": "widget.WidgetPair", "widget1": RoundWidget(), "widget2": {"_cls": "widget.RoundWidget"}},
    )
    assert pair.cfg["widget1"].cfg["radius"] == 1
    assert pair.cfg["widget2"].cfg["radius"] == 1


def test_instantiate_object_new_defaults():
    pair = instantiate_object({"_cls": "widget.WidgetPair"})
    assert pair.cfg["widget1"].name == "widget.RectangleWidget"
    assert pair.cfg["widget2"].name == "widget.RectangleWidget"

    pair = instantiate_object({"_cls": "widget.WidgetPair", "*": {"widget1": {"_cls": "widget.RoundWidget", "radius": 2}}})
    assert pair.cfg["widget1"].name == "widget.RoundWidget"
    assert pair.cfg["widget1"].cfg["radius"] == 2

    pair = instantiate_object({"_cls": "widget.WidgetPair", "*": {"widget1": RoundWidget(5)}})
    assert pair.cfg["widget1"].name == "widget.RoundWidget"
    assert pair.cfg["widget1"].cfg["radius"] == 5


def test_cache_str():
    pair = instantiate_object(
        {"_cls": "widget.WidgetPair", "widget1": RoundWidget(2), "widget2": {"_cls": "widget.RoundWidget", "radius": 3}},
    )
    assert (
        pair.cache_str()
        == '{"_cls": "widget.WidgetPair", "widget1": {"_cls": "widget.RoundWidget", "radius": 2}, "widget2": {"_cls": "widget.RoundWidget", "radius": 3.0}}'
    )

    pair = instantiate_object(
        {"_cls": "widget.WidgetPair", "widget1": None, "widget2": {"_cls": "widget.RoundWidget", "radius": 3}},
    )
    assert (
        pair.cache_str()
        == '{"_cls": "widget.WidgetPair", "widget1": null, "widget2": {"_cls": "widget.RoundWidget", "radius": 3.0}}'
    )


def test_main(tmp_path):
    wp_area, rw_area = WidgetPair.area, RoundWidget.area
    WidgetPair.area = cacheable(NumpyOutput)(WidgetPair.area)
    RoundWidget.area = cacheable(NumpyOutput)(RoundWidget.area)

    first = f"skip-first-arg widget.WidgetPair area extra=1 --output {tmp_path} "
    cfg = " --config widget1._cls=widget.RoundWidget widget2._cls=widget.RoundWidget widget2.radius=0"
    out = __main__((first + cfg).split())
    assert out == 7

    first = f"skip-first-arg widget.WidgetPair widget2.area extra=1 --output {tmp_path} --log-artifacts "
    out = __main__((first + cfg).split())
    assert out == 1

    first = f"skip-first-arg widget.WidgetPair widget2.area extra=1 --output {tmp_path} --rm "
    out = __main__((first + cfg).split())

    first = f"skip-first-arg widget.WidgetPair widget2.area extra=123456789 --output {tmp_path} --rm "
    out = __main__((first + cfg).split())

    first = f"skip-first-arg widget.WidgetPair widget2.area extra=1 --output {tmp_path} --get-path "
    out = __main__((first + cfg).split())

    fn = tmp_path / "kwargs.pkl"
    with open(fn, "wb") as outf:
        pickle.dump({"extra": 3.0}, outf)
    first = f"skip-first-arg widget.WidgetPair widget2.area from_pkl={fn} --output {tmp_path} "
    out = __main__((first + cfg).split())
    assert out == 3

    with pytest.raises(RuntimeError):
        __main__((f"skip-first-arg widget.WidgetPair area INVALIDARG=1 area=2 --output {tmp_path} " + cfg).split())

    WidgetPair.area, RoundWidget.area = wp_area, rw_area


def test_instantiate_minimal_class():
    class MinimalIngredient:
        @configurable
        def __init__(self, x: int = 1, s=1):
            pass

    x1 = instantiate_object({"_cls": MinimalIngredient})
    assert x1.cfg["x"] == 1
    assert x1.cfg["s"] == 1
    x2 = instantiate_object({"_cls": MinimalIngredient, "x": 2})
    assert x2.cfg["x"] == 2
    x3 = instantiate_object({"_cls": MinimalIngredient, "x": "3", "s": "1"})
    assert x3.cfg["x"] == 3
    assert x3.cfg["s"] == "1"


def test_instantiate_nested_minimal_class():
    class WithoutConfigurable:
        def __init__(self, z=1):
            self.z = z

    class AlmostMinimalIngredient:
        @configurable
        def __init__(self, x: int = 1, obj=None):
            pass

    ing = instantiate_object({"_cls": AlmostMinimalIngredient, "obj": {"_cls": AlmostMinimalIngredient, "x": 2}})
    assert ing.cfg["x"] == 1
    assert ing.cfg["obj"].cfg["x"] == 2
    assert ing.cfg["obj"].cfg["obj"] is None

    ing = instantiate_object({"_cls": AlmostMinimalIngredient, "obj": AlmostMinimalIngredient(x=3, obj=4)})
    assert ing.cfg["x"] == 1
    assert ing.cfg["obj"].cfg["x"] == 3
    assert ing.cfg["obj"].cfg["obj"] == 4

    ing = instantiate_object({"_cls": AlmostMinimalIngredient, "obj": WithoutConfigurable(z=1)})
    assert isinstance(ing.cfg["obj"], WithoutConfigurable)
    assert ing.cfg["obj"].z == 1

    ing = instantiate_object({"_cls": AlmostMinimalIngredient, "obj": {"_cls": WithoutConfigurable, "z": 2}})
    assert isinstance(ing.cfg["obj"], WithoutConfigurable)
    assert ing.cfg["obj"].z == 2

    ing = instantiate_object(
        {"_cls": AlmostMinimalIngredient, "obj": {"_cls": WithoutConfigurable, "z": {"_cls": WithoutConfigurable}}}
    )
    assert isinstance(ing.cfg["obj"], WithoutConfigurable)
    assert isinstance(ing.cfg["obj"].z, WithoutConfigurable)
    assert not hasattr(ing.cfg["obj"], "cfg")
