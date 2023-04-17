from pathlib import Path
from typing import Any, List

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
    def dump_storage_tree(path: Path) -> List[str]:
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
    def dump_object(obj: Any) -> Any:
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
            val1 = getattr(obj1, f.name)
            val2 = getattr(obj2, f.name)

            if is_array(f.type):
                if val2 is None:
                    assert val1 == val2
                elif isinstance(val2, List) and len(val2) > 0 and "__attrs_attrs__" in dir(val2[0]):
                    for index in range(len(val2)):
                        Helpers.assert_equal(val1[index], val2[index])
                else:
                    objs_equal = val1 == val2

                    try:
                        assert all(objs_equal)
                    except ValueError:
                        assert objs_equal.all()
                    except TypeError:
                        assert objs_equal
            else:
                assert val1 == val2
