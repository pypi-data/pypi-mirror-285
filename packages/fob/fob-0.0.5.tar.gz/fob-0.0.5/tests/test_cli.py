import os

import pytest

from fob.cli import parse_args, config_list_to_dict, config_string_to_dict, config_dict_to_string, update_dict


def test_parse_args():
    examples = {
        "task.foo eps=42 --output bar --search-path --rm": {
            "cls": "task.foo",
            "cmd": None,
            "cmd_args": ["eps=42"],
            "options": {"--rm": "", "--output": "bar", "--search-path": None},
            "cls_config": [],
        },
        "task.rerank.Rerank benchmark.collection.stats ca=SomeArg --get-path --search-path foo --config benchmark.collection.name=foo benchmark.thing=xyz": {
            "cls": "task.rerank.Rerank",
            "cmd": "benchmark.collection.stats",
            "cmd_args": ["ca=SomeArg"],
            "options": {"--get-path": "", "--search-path": "foo"},
            "cls_config": ["benchmark.collection.name=foo", "benchmark.thing=xyz"],
        },
    }

    for argstr, d in examples.items():
        assert parse_args(argstr.split(), bool_options=["--get-path", "--rm"]) == d

    with pytest.raises(ValueError):
        parse_args(["--bad-option"])


def test_config_list_to_dict():
    args = ["foo.bar=yes", " ", "main=42", "  \n "]
    assert config_list_to_dict(args) == {"foo": {"bar": "yes"}, "main": "42"}

    args = ["foo.bar=yes", "main=42", "foo.bar=override"]
    assert config_list_to_dict(args) == {"foo": {"bar": "override"}, "main": "42"}

    for invalid in ["inv", ".inv", "inv.", "inv=", "inv.=1", ".inv=1"]:
        args = [invalid]
        with pytest.raises(ValueError):
            config_list_to_dict(args)


def test_config_string_to_dict():
    s = "foo.bar=yes   main=42  \n  "
    assert config_string_to_dict(s) == {"foo": {"bar": "yes"}, "main": "42"}


def test_config_string_to_dict_with_object_lists():
    s = """
           mine1=222
           foo.bar=yes
           foo.stuff._cls=stuffcls.WrongThing
           foo.stuff.val=999999999
           foo.stuff._cls,=stuffcls.Thing
           foo.stuff._cls,=stuffcls.Thing
           foo.stuff.val=123
           foo.stuff._cls,=stuffcls.Thing
           foo.stuff.val=456
           foo.another=123
           foo.more._cls,=again.Again
           foo.more._cls,=again.YetAgain
           foo.more._cls,=again.Again
           foo.more.status=last
           mine2=444
       """

    correct = {
        "mine1": "222",
        "foo": {
            "bar": "yes",
            "stuff": [
                {"_cls": "stuffcls.Thing"},
                {"_cls": "stuffcls.Thing", "val": "123"},
                {"_cls": "stuffcls.Thing", "val": "456"},
            ],
            "another": "123",
            "more": [{"_cls": "again.Again"}, {"_cls": "again.YetAgain"}, {"_cls": "again.Again", "status": "last"}],
        },
        "mine2": "444",
    }

    assert config_string_to_dict(s) == correct


def test_config_string_to_dict_with_object_lists_and_files(tmpdir):
    s = f"""
           mine1=222
           foo.bar=yes
           foo.stuff._cls=stuffcls.WrongThing
           foo.stuff.val=999999999
           foo.stuff.file,={tmpdir / "file1"}
           foo.stuff._cls,=stuffcls.Thing
           foo.stuff.val=456
           foo.slightdiff.file={tmpdir / "file1"}
           foo.slightdiff._cls,=slightdiffcls.Thing
           foo.slightdiff.val=456
           foo.another=123
           foo.more._cls,=again.Again
           foo.more._cls,=again.YetAgain
           foo.more._cls,=again.Again
           foo.more.status=last
           mine2=444
           """

    FILE1 = """
           _cls=stuffcls.Thing
           _cls,=stuffcls.Thing
           val=123
           """
    with open(tmpdir / "file1", "wt", encoding="utf-8") as outf:
        print(FILE1, file=outf)

    correct = {
        "mine1": "222",
        "foo": {
            "bar": "yes",
            "stuff": [
                {"_cls": "stuffcls.Thing"},
                {"_cls": "stuffcls.Thing", "val": "123"},
                {"_cls": "stuffcls.Thing", "val": "456"},
            ],
            "slightdiff": [
                {"_cls": "stuffcls.Thing", "val": "123"},
                {"_cls": "slightdiffcls.Thing", "val": "456"},
            ],
            "another": "123",
            "more": [{"_cls": "again.Again"}, {"_cls": "again.YetAgain"}, {"_cls": "again.Again", "status": "last"}],
        },
        "mine2": "444",
    }

    assert config_string_to_dict(s) == correct


def test_config_string_with_files_to_dict(tmpdir):
    mainfn = os.path.join(tmpdir, "main.txt")
    with open(mainfn, "wt") as f:
        print("main=24  # comment", file=f)
        print("#main=25", file=f)

    foofn = os.path.join(tmpdir, "foo.txt")
    with open(foofn, "wt") as f:
        print("test1=20  submod1.test1=21 ", file=f)
        print("submod1.submod2.test1=22", file=f)
        print("test3=extra", file=f)
        print(f"FILE={mainfn}", file=f)

    args = ["foo.test1=1", f"foo.file={foofn}", "main=42", f"file={mainfn}"]
    assert config_list_to_dict(args) == {
        "foo": {"test1": "20", "test3": "extra", "main": "24", "submod1": {"test1": "21", "submod2": {"test1": "22"}}},
        "main": "24",
    }


def test_simple_config_dict_to_string():
    d = {"foo": 1, "_cls": "bar"}
    dset = set(config_dict_to_string(d).split(" "))
    assert len(dset) == 2
    assert "foo=1" in dset
    assert "_cls=bar" in dset


def test_nested_config_dict_to_string():
    thing1 = {"_cls": "thing1", "val": 123}
    thing2 = {"_cls": "thingparent", "child": {"val": 1, "grandchild": {"val": 0}}}
    d = {"foo": 1, "_cls": "bar", "thing1": thing1, "thing2": thing2}
    dset = set(config_dict_to_string(d).split(" "))
    assert len(dset) == 7
    assert "foo=1" in dset
    assert "_cls=bar" in dset
    assert "thing1._cls=thing1" in dset
    assert "thing1.val=123" in dset
    assert "thing2._cls=thingparent" in dset
    assert "thing2.child.val=1" in dset
    assert "thing2.child.grandchild.val=0" in dset


def test_update_dict():
    d1 = {1: 2, 3: {4: 5, 8: 9, 10: {"foo": {"bar": 123}}}}
    d2 = {1: 3, 3: {4: 5, 8: 10, 10: {99: 100}, 22: 23}}

    combined = {1: 3, 3: {4: 5, 8: 10, 22: 23, 10: {99: 100, "foo": {"bar": 123}}}}
    update_dict(d1, d2)
    assert d1 == combined
