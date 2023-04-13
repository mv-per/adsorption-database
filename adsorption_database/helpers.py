from pathlib import Path
from typing import Any


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
