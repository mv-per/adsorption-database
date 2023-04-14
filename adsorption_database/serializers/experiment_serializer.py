from typing import Any, List, Optional
from attr import fields

import numpy as np
from adsorption_database.models.adsorbate import Adsorbate
from h5py import Group, SoftLink
import numpy.typing as npt
from adsorption_database.models.adsorbent import Adsorbent
from adsorption_database.models.experiment import Experiment

from adsorption_database.models.isotherms import MixIsotherm, MonoIsotherm
from adsorption_database.serializers.abstract_serializer import AbstractSerializer


class ExperimentSerializer(AbstractSerializer):
    def __init__(self) -> None:
        super().__init__(Experiment)

    def get_attributes(self):
        return [
            field.name
            for field in fields(self._model_class)
            if field.type not in [Adsorbent, List[MonoIsotherm], List[MixIsotherm]]
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
