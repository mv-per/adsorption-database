# pragma: no cover
from typing import Any, Dict, List
from attr import fields


from adsorption_database.defaults import MONO_ISOTHERMS, MIXTURE_ISOTHERMS

from h5py import Group

from adsorption_database.models.adsorbent import Adsorbent
from adsorption_database.models.experiment import Experiment

from adsorption_database.models.isotherms import (
    MixIsotherm,
    MonoIsotherm,
)
from adsorption_database.serializers.abstract_serializer import (
    AbstractSerializer,
)
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.mix_isotherm_serializer import (
    MixIsothermSerializer,
)
from adsorption_database.serializers.mono_isotherm_serializer import (
    MonoIsothermSerializer,
)
from adsorption_database.shared import (
    get_adsorbent_group_route,
    get_attr_fields_from_infos,
    get_root_group,
)


class ExperimentSerializer(AbstractSerializer):
    def __init__(self) -> None:
        super().__init__(Experiment)

    def get_attributes(self):
        return [
            (field.name, field.type)
            for field in fields(self._model_class)
            if field.type
            not in [Adsorbent, List[MonoIsotherm], List[MixIsotherm]]
        ]

    def get_datasets(self):
        return []

    def load(self, group: Group) -> Any:

        _fields: Dict[str, Any] = {}
        attributes = self.get_attributes()
        get_attr_fields_from_infos(_fields, attributes, group)

        if MONO_ISOTHERMS in list(group):
            _fields["monocomponent_isotherms"] = []
            for isotherm_name in list(group[MONO_ISOTHERMS]):
                isotherm_group = group[MONO_ISOTHERMS].get(isotherm_name)
                if isotherm_group is None:
                    continue
                mono_isotherm = MonoIsothermSerializer().load(isotherm_group)
                _fields["monocomponent_isotherms"].append(mono_isotherm)

        if MIXTURE_ISOTHERMS in list(group):
            _fields["mixture_isotherms"] = []
            for isotherm_name in list(group[MIXTURE_ISOTHERMS]):
                isotherm_group = group[MIXTURE_ISOTHERMS].get(isotherm_name)
                if isotherm_group is None:
                    continue
                mix_isotherm = MixIsothermSerializer().load(isotherm_group)
                _fields["mixture_isotherms"].append(mix_isotherm)

        if "adsorbent" in list(group.attrs):
            root_group = get_root_group(group)
            adsorbent_group = root_group.get(group.attrs["adsorbent"])
            if adsorbent_group is not None:
                _fields["adsorbent"] = AttrOnlySerializer(Adsorbent).load(
                    adsorbent_group
                )

        obj = self._model_class(**_fields)

        return obj

    def dump(self, obj: Experiment, group: Group) -> None:

        attributes = self.get_attributes()
        attribute_names = [attr[0] for attr in attributes]

        self._register_attributes(attribute_names, obj, group)

        route = get_adsorbent_group_route(obj.adsorbent.name)
        group.attrs["adsorbent"] = route
