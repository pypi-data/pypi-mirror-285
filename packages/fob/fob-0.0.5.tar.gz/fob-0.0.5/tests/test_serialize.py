import os

import numpy as np

from fob.serialize import DictNumpyOutput, NumpyOutput, JsonOutput, PickleOutput, TRECRunOutput, StringOutput, TemporaryOutputPath


def test_numpyoutput(tmp_path):
    data = np.array([1, 2, 3])
    data2 = NumpyOutput.serialize(data, tmp_path)
    assert all(data == data2)
    assert all(NumpyOutput.deserialize(tmp_path) == data)


def test_dictnumpyoutput(tmp_path):
    data = np.array([[1, 2], [3, 4]])
    ids = np.array(["d1", "d2"])

    d = {"ids": ids, "data": data}

    serialized = DictNumpyOutput.serialize(d, tmp_path)
    assert (serialized["ids"] == ids).all()
    assert (serialized["data"] == data).all()

    deser = DictNumpyOutput.deserialize(tmp_path)
    assert (deser["ids"] == ids).all()
    assert (deser["data"] == data).all()


def test_trecrunoutput(tmp_path):
    from trecrun import TRECRun

    data = TRECRun({1: {"d1": 1, "d2": 1.5}})
    data2 = TRECRunOutput.serialize(data, tmp_path)
    assert data == data2
    assert TRECRunOutput.deserialize(tmp_path) == data


def test_jsonoutput(tmp_path):
    data = {"k1": 2, "k2": [4, 5, 6]}
    data2 = JsonOutput.serialize(data, tmp_path)
    assert data == data2
    assert JsonOutput.deserialize(tmp_path) == data


def test_pickleoutput(tmp_path):
    data = {1: 2, 3: [4, 5, 6]}
    data2 = PickleOutput.serialize(data, tmp_path)
    assert data == data2
    assert PickleOutput.deserialize(tmp_path) == data


def test_stringoutput(tmp_path):
    data = "ahem"
    data2 = StringOutput.serialize(data, tmp_path)
    assert data == data2
    assert StringOutput.deserialize(tmp_path) == data


def test_temporary_output_path_unique(tmp_path):
    tmp_path_context = lambda: TemporaryOutputPath(tmp_path)
    for _ in range(100):
        with tmp_path_context() as path:
            assert not os.path.exists(path)
            os.makedirs(path, exist_ok=False)
