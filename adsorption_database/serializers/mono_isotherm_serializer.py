from typing import Any, Dict, Optional
from attr import fields

import numpy as np
from adsorption_database.models.adsorbate import Adsorbate
from h5py import Group
import numpy.typing as npt

from adsorption_database.models.isotherms import MonoIsotherm
from adsorption_database.serializers.abstract_serializer import (
    AbstractSerializer,
)
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.shared import (
    get_adsorbate_group_route,
    get_attr_fields_from_infos,
    get_dataset_fields,
    get_root_group,
)


class MonoIsothermSerializer(AbstractSerializer):
    def __init__(self) -> None:
        super().__init__(MonoIsotherm)

    def get_attributes(self):
        return [
            (field.name, field.type)
            for field in fields(self._model_class)
            if field.type
            not in [
                npt.NDArray[np.float64],
                Adsorbate,
                Optional[npt.NDArray[np.float64]],
            ]
        ]

    def get_datasets(self):
        return [
            field.name
            for field in fields(self._model_class)
            if field.type
            in [npt.NDArray[np.float64], Optional[npt.NDArray[np.float64]]]
        ]

    def load(self, group: Group) -> Any:

        _fields: Dict[str, Any] = {}

        attributes = self.get_attributes()
        get_attr_fields_from_infos(_fields, attributes, group)

        dataset_names = self.get_datasets()
        get_dataset_fields(_fields, dataset_names, group)

        if "adsorbate" in list(group.attrs):
            root_group = get_root_group(group)
            adsorbate_group = root_group.get(group.attrs["adsorbate"])
            _fields["adsorbate"] = AttrOnlySerializer(Adsorbate).load(
                adsorbate_group
            )

        obj = self._model_class(**_fields)

        return obj

    def dump(self, obj: Any, group: Group) -> None:

        attributes = self.get_attributes()
        attribute_names = [attribute[0] for attribute in attributes]

        self._register_attributes(attribute_names, obj, group)

        dataset_names = self.get_datasets()

        self._register_datasets(dataset_names, obj, group)

        route = get_adsorbate_group_route(obj.adsorbate.name)
        group.attrs["adsorbate"] = route
