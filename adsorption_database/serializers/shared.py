from attr import fields
import numpy as np
from adsorption_database.defaults import ADSORBATES
from typing import Any, Dict, List, Tuple, Type
from h5py import Group
import numpy.typing as npt
import numpy as np


def get_adsorbate_group_route(adsorbate_name: str):
    return f"/{ADSORBATES}/{adsorbate_name}"


def get_valid_type(args: List[Type]) -> Type:
    NoneType = type(None)
    return [arg for arg in args if arg != NoneType][0]


def get_attr_fields_from_infos(
    fields: Dict[str, Any], attribute_infos: List[Tuple[str, Type]], group: Group
) -> None:
    for (attribute, _type) in attribute_infos:
        val = group.attrs.get(attribute)
        if val is not None:
            try:
                val = _type(val)
            except TypeError:
                # some attrs are optional, this gets its valid type
                valid_type = get_valid_type(_type.__args__)
                val = valid_type(val)

        fields[attribute] = val


def get_dataset_fields(fields: Dict[str, Any], dataset_names: List[str], group: Group) -> None:

    for dataset_name in dataset_names:
        val = group.get(dataset_name)
        if val is None:
            continue
        fields[dataset_name] = np.array(val)


def assert_equal(obj1: Any, obj2: Any) -> None:

    _fields = fields(type(obj1))

    for f in _fields:
        if f.type == npt.NDArray[np.float64]:
            assert (getattr(obj2, f.name) == getattr(obj1, f.name)).all()
        else:
            assert getattr(obj2, f.name) == getattr(obj1, f.name)
