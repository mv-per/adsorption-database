from pathlib import Path
from typing import Any, List
import numpy.typing as npt

from attr import fields


def is_array(_type: Any) -> bool:

    if "List" in str(_type) or "numpy.float64" in str(_type):
        return True
    else:
        str_args = [str(arg) for arg in _type.__args__]
        for arg in str_args:
            if "numpy.float64" in arg:
                return True
        return False


class Helpers:
    @staticmethod
    def dump_storage_tree(path: Path):
        import subprocess

        return (
            subprocess.run(
                ["h5dump", f"{path.name}"],
                cwd=path.parent.resolve(),
                capture_output=True,
                text=True,
            )
            .stdout.strip("\n")
            .split("\n")
        )

    @staticmethod
    def dump_object(obj: Any) -> str:
        import jsonpickle

        import jsonpickle.ext.numpy as jsonpickle_numpy

        jsonpickle.set_encoder_options("simplejson")

        jsonpickle_numpy.register_handlers()

        pickler = jsonpickle.pickler.Pickler()

        return pickler.flatten(obj)

    @staticmethod
    def assert_equal(obj1: Any, obj2: Any) -> None:

        _fields = fields(type(obj1))

        for f in _fields:
            try:
                _is_array = is_array(f.type)
            except AttributeError:
                _is_array = False

            if _is_array:
                val = getattr(obj2, f.name)
                if val is None:
                    assert getattr(obj2, f.name) == getattr(obj1, f.name)
                elif isinstance(val, List) and "__attrs_attrs__" in dir(
                    val[0]
                ):  # check if this is an attrs class
                    for index in range(len(val)):
                        Helpers.assert_equal(val[index], getattr(obj1, f.name)[index])
                else:
                    _objs = getattr(obj2, f.name) == getattr(obj1, f.name)

                    try:
                        _arr = [__obj for __obj in _objs]
                        assert all(_arr)
                    except ValueError:
                        assert _objs.all()
                    except TypeError:
                        assert _objs
            else:
                assert getattr(obj2, f.name) == getattr(obj1, f.name)
