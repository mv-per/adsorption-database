from typing import Any, Dict, List
from attr import fields

import numpy as np
from adsorption_database.defaults import MIXTURE_ISOTHERMS
from adsorption_database.models.adsorbate import Adsorbate
from h5py import Group
import numpy.typing as npt

from adsorption_database.models.isotherms import MixIsotherm, MonoIsotherm
from adsorption_database.serializers.abstract_serializer import (
    AbstractSerializer,
)
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.mono_isotherm_serializer import (
    get_root_group,
)
from adsorption_database.shared import (
    get_adsorbate_group_route,
    get_attr_fields_from_infos,
    get_dataset_fields,
)


class MixIsothermSerializer(AbstractSerializer):
    def __init__(self) -> None:
        super().__init__(MixIsotherm)

    def get_attributes(self):
        return [
            (field.name, field.type)
            for field in fields(self._model_class)
            if field.type not in [npt.NDArray[np.float64], List[Adsorbate]]
        ]

    def get_datasets(self):
        return [
            field.name
            for field in fields(self._model_class)
            if field.type in [npt.NDArray[np.float64]]
        ]

    def load(self, group: Group) -> Any:

        _fields: Dict[str, Any] = {}

        attributes = self.get_attributes()
        get_attr_fields_from_infos(_fields, attributes, group)

        dataset_names = self.get_datasets()
        get_dataset_fields(_fields, dataset_names, group)

        if "adsorbates" in list(group.attrs):
            root_group = get_root_group(group)
            _fields["adsorbates"] = []
            adsorbate_serializer = AttrOnlySerializer(Adsorbate)
            for adsorbate in group.attrs["adsorbates"]:
                adsorbate_group = root_group.get(adsorbate)
                _fields["adsorbates"].append(
                    adsorbate_serializer.load(adsorbate_group)
                )

        obj = self._model_class(**_fields)

        return obj

    def dump(self, obj: Any, group: Group) -> None:

        attributes = self.get_attributes()
        attribute_names = [attr[0] for attr in attributes]

        self._register_attributes(attribute_names, obj, group)

        dataset_names = self.get_datasets()

        self._register_datasets(dataset_names, obj, group)

        # Since h5py still doesn't support storing arrays with object type, for mixtures we store the
        # full path to the adsorbate. In doing this, on de-serializing the stored object, the code must
        # check whether the adsorbate still exists in the storage
        group.attrs["adsorbates"] = np.array(
            [
                str.encode(get_adsorbate_group_route(adsorbate.name))
                for adsorbate in obj.adsorbates
            ]
        )
