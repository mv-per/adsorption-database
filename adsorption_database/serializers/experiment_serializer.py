from typing import Any, Dict, List
from attr import fields
import numpy as np


from adsorption_database.defaults import MONO_ISOTHERMS, MIXTURE_ISOTHERMS

from h5py import Group

from adsorption_database.models.adsorbent import Adsorbent
from adsorption_database.models.experiment import Experiment

from adsorption_database.models.isotherms import Isotherm, MixIsotherm, MonoIsotherm
from adsorption_database.serializers.abstract_serializer import AbstractSerializer
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.mix_isotherm_serializer import MixIsothermSerializer
from adsorption_database.serializers.mono_isotherm_serializer import MonoIsothermSerializer
from adsorption_database.serializers.shared import get_adsorbent_group_route, get_attr_fields_from_infos, get_root_group


class ExperimentSerializer(AbstractSerializer):
    def __init__(self) -> None:
        super().__init__(Experiment)

    def get_attributes(self):
        return [
            (field.name, field.type)
            for field in fields(self._model_class)
            if field.type not in [Adsorbent, List[MonoIsotherm], List[MixIsotherm]]
        ]

    def load(self, group: Group) -> Any:

        _fields: Dict[str, Any] = {}
        attributes = self.get_attributes()
        get_attr_fields_from_infos(_fields, attributes, group)

        if "monocomponent_isotherms" in list(group.attrs):
            _fields["monocomponent_isotherms"] = []
            for mono_isotherm in group.attrs["monocomponent_isotherms"]:
                isotherm_group = group.get(mono_isotherm)
                if isotherm_group is None:
                    continue
                mono_isotherm = MonoIsothermSerializer().load(isotherm_group)
                _fields["monocomponent_isotherms"].append(mono_isotherm)

        if "mixture_isotherms" in list(group.attrs):
            _fields["mixture_isotherms"] = []
            for mono_isotherm in group.attrs["mixture_isotherms"]:
                isotherm_group = group.get(mono_isotherm)
                if isotherm_group is None:
                    continue
                mono_isotherm = MixIsothermSerializer().load(isotherm_group)
                _fields["mixture_isotherms"].append(mono_isotherm)

        if "adsorbent" in list(group.attrs):
            root_group = get_root_group(group)
            adsorbent_group = root_group.get(group.attrs["adsorbent"])
            if adsorbent_group is not None:
                _fields["adsorbent"] = AttrOnlySerializer(Adsorbent).load(adsorbent_group)
            

        obj = self._model_class(**_fields)

        return obj

    def dump(self, obj: Experiment, group: Group) -> None:

        attributes = self.get_attributes()
        attribute_names = [attr[0] for attr in attributes]

        self._register_attributes(attribute_names, obj, group)

        def get_isotherm_pathnames(isotherms: List[Isotherm], main_path: str) -> List[str]:
            return [str.encode(main_path + "/" + isotherm.name) for isotherm in isotherms]

        moncomponent_isotherm_names = get_isotherm_pathnames(
            obj.monocomponent_isotherms, MONO_ISOTHERMS
        )
        mixture_isotherms_names = get_isotherm_pathnames(obj.mixture_isotherms, MIXTURE_ISOTHERMS)

        group.attrs["monocomponent_isotherms"] = np.array(moncomponent_isotherm_names)
        group.attrs["mixture_isotherms"] = np.array(mixture_isotherms_names)

        route = get_adsorbent_group_route(obj.adsorbent.name)
        group.attrs["adsorbent"] = route
