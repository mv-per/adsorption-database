import numpy as np
from adsorption_database.defaults import (
    ADSORBATES,
    ADSORBENTS,
    EXPERIMENTS,
    MIXTURE_ISOTHERMS,
    MONO_ISOTHERMS,
)
from typing import Any, Dict, List, Tuple, Type
from h5py import Group
from adsorption_database.helpers import Helpers

from adsorption_database.models.isotherms import Isotherm
from adsorption_database.storage_provider import StorageProvider


def get_root_group(group: Group) -> Group:
    "recursively searches for the parent group"
    if group.name == "/":
        return group
    else:
        return get_root_group(group.parent)


def get_adsorbate_group_route(adsorbate_name: str) -> str:
    return f"/{ADSORBATES}/{adsorbate_name}"


def get_adsorbent_group_route(name: str) -> str:
    return f"/{ADSORBENTS}/{name}"


def get_valid_type(args: List[Type]) -> Type:
    NoneType = type(None)

    return [arg for arg in args if arg != NoneType][0]


def get_attr_fields_from_infos(
    fields: Dict[str, Any],
    attribute_infos: List[Tuple[str, Type]],
    group: Group,
) -> None:
    for (attribute, _type) in attribute_infos:
        val = group.attrs.get(attribute)
        if val is not None:
            try:
                val = _type(val)
            except TypeError:
                # some attrs are optional, this gets its valid type
                valid_type = get_valid_type(_type.__args__)

                if "List" in str(valid_type):
                    valid_type = list

                val = valid_type(val)

        fields[attribute] = val


def get_dataset_fields(
    fields: Dict[str, Any], dataset_names: List[str], group: Group
) -> None:

    for dataset_name in dataset_names:
        val = group.get(dataset_name)
        if val is None:
            continue
        fields[dataset_name] = np.array(val)


def get_mono_isotherm_group(experiment_group: Group) -> Group:
    """
    Get the group object for storing pure component isotherm data.

    This method retrieves the HDF5 group object for storing pure component isotherm data within an experiment
    group. The group object is retrieved based on a predefined group name.

    Args:
        experiment_group (Group): The experiment group object within which to get the pure component isotherm group.

    Returns:
        Group: The group object for storing pure component isotherm data.
    """
    return experiment_group.require_group(MONO_ISOTHERMS)


def get_experiments_group(group: Group) -> Group:
    """
    Get the group object for storing pure component isotherm data.

    This method retrieves the HDF5 group object for storing pure component isotherm data within an experiment
    group. The group object is retrieved based on a predefined group name.

    Args:
        experiment_group (Group): The experiment group object within which to get the pure component isotherm group.

    Returns:
        Group: The group object for storing pure component isotherm data.
    """
    root_group = get_root_group(group)
    return root_group.require_group(EXPERIMENTS)


def get_mix_isotherm_group(experiment_group: Group) -> Group:
    """
    Get the group object for storing mixture isotherm data.

    This method retrieves the HDF5 group object for storing mixture isotherm data within an experiment
    group. The group object is retrieved based on a predefined group name.

    Args:
        experiment_group (Group): The experiment group object within which to get the mixture isotherm group.

    Returns:
        Group: The group object for storing mixture isotherm data.
    """
    return experiment_group.require_group(MIXTURE_ISOTHERMS)


def get_isotherm_store_name(isotherm: Isotherm) -> str:
    """
    Get the store name for an isotherm object.

    This method generates a unique store name for an isotherm object based on its name and type. The
    generated store name is a string combining the isotherm's name and type with a hyphen separator.

    Args:
        isotherm (Union[MixIsotherm, MonoIsotherm]): The isotherm object for which to generate the store name.

    Returns:
        str: The generated store name.
    """
    return f"{isotherm.name}-{isotherm.isotherm_type.value}"


def gen_regression() -> None:
    import json

    path = StorageProvider().get_file_path()
    regression = Helpers().dump_storage_tree(path)

    data = {"data": regression}
    with open(path.parent.resolve() / "storage_regression.json", "w") as f:
        json.dump(data, f)
