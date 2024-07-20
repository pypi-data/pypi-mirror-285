from fob import Ingredient

import pytest

from typing import List, Type, Union

from fob.types import (
    simple_type_annotation_to_type,
    cast_dict_to_types,
    cast_string_to_type,
    convert_string_to_list,
    primitive_config_types,
    annotation_to_typef,
)


def test_convert_string_to_list():
    # test typed conversions
    assert convert_string_to_list("1,2", int) == [1, 2]
    assert convert_string_to_list("1", int) == [
        1,
    ]
    assert convert_string_to_list("1.1,1.2", float) == [1.1, 1.2]
    assert convert_string_to_list("1.1", float) == [
        1.1,
    ]
    assert convert_string_to_list("1,2", str) == ["1", "2"]
    assert convert_string_to_list("1", str) == [
        "1",
    ]

    # test range conversions
    assert convert_string_to_list("1..4,1", int) == [1, 2, 3, 4]
    assert convert_string_to_list("1..4,0.5", float) == [1, 1.5, 2, 2.5, 3, 3.5, 4.0]
    assert convert_string_to_list("0.65..0.8,0.05", float) == [0.65, 0.7, 0.75, 0.80]
    assert convert_string_to_list("0.00001..0.00002,2e-06", float) == [1e-05, 1.2e-05, 1.4e-05, 1.6e-05, 1.8e-05, 2.0e-05]

    # test range checking endpoints
    assert convert_string_to_list("1,2,3,4,6", int) == [1, 2, 3, 4, 6]
    assert convert_string_to_list("0,2,3,4,5", int) == [0, 2, 3, 4, 5]

    # nothing happens if the input is not a str
    assert convert_string_to_list(1, int) == 1
    assert convert_string_to_list(1, str) == 1

    with pytest.raises(ValueError):
        convert_string_to_list("5..4,1", float)

    with pytest.raises(ValueError):
        convert_string_to_list("3..1,1", int)


def test_simple_type_annotation_to_type():
    for typef in primitive_config_types - {None}:
        assert simple_type_annotation_to_type(typef) == (False, annotation_to_typef.get(typef, typef), typef)
        print("FFS", simple_type_annotation_to_type(List[typef]))
        assert simple_type_annotation_to_type(List[typef]) == (
            True,
            annotation_to_typef.get(typef, typef),
            typef,
        )
        assert simple_type_annotation_to_type(Union[typef, List[typef]]) == (
            True,
            annotation_to_typef.get(typef, typef),
            typef,
        )


def test_cast_string_to_type():
    assert cast_string_to_type("1", str) == "1"
    assert cast_string_to_type("1", float) == 1.0
    assert cast_string_to_type("1", int) == 1
    assert cast_string_to_type("1", bool) is True

    assert cast_string_to_type("1", List[str]) == ["1"]
    assert cast_string_to_type("1", List[float]) == [1.0]
    assert cast_string_to_type("1", List[int]) == [1]
    assert cast_string_to_type("1", List[bool]) == [True]

    assert cast_string_to_type("1,2,1", List[str]) == ["1", "2", "1"]
    assert cast_string_to_type("1,2,1", List[float]) == [1.0, 2.0, 1.0]
    assert cast_string_to_type("1,2,1", List[int]) == [1, 2, 1]


def test_cast_dict_to_types():
    d = {"anint": "1", "afloat": "2.3", "obj": "None", "ing": None, "wrongAnnotation": None}
    annotations = {"anint": int, "afloat": float, "ing": Type[Ingredient], "wrongAnnotation": Ingredient}
    castd = cast_dict_to_types(d, annotations)
    assert type(castd["anint"]) == int
    assert type(castd["afloat"]) == float
    assert castd["obj"] == None
    assert castd["ing"] == None
