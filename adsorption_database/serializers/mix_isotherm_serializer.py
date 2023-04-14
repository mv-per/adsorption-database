from typing import Any, List, Optional
from attr import fields

import numpy as np
from adsorption_database.defaults import ADSORBATES
from adsorption_database.models.adsorbate import Adsorbate
from h5py import Group, SoftLink
import numpy.typing as npt

from adsorption_database.models.isotherms import MixIsotherm, MonoIsotherm
from adsorption_database.serializers.abstract_serializer import AbstractSerializer
from adsorption_database.serializers.shared import get_adsorbate_group_route


class MixIsothermSerializer(AbstractSerializer):
    def __init__(self) -> None:
        super().__init__(MixIsotherm)

    def get_attributes(self):
        return [
            field.name
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

        attributes = self.get_attributes()
        obj = self._model_class()

        for attribute in attributes:
            setattr(obj, attribute, getattr(group.attrs, attribute, None))

        return obj

    def dump(self, obj: Any, group: Group) -> None:

        attributes = self.get_attributes()

        self._register_attributes(attributes, obj, group)

        dataset_names = self.get_datasets()

        self._register_datasets(dataset_names, obj, group)

        # Since h5py still doesn't support storing arrays with object type, for mixtures we store the
        # full path to the adsorbate. In doing this, on de-serializing the stored object, the code must
        # check whether the adsorbate still exists in the storage
        if "adsorbates" in list(group):
            del group["adsorbates"]
        group["adsorbates"] = np.array(
            [str.encode(get_adsorbate_group_route(adsorbate.name)) for adsorbate in obj.adsorbates]
        )
