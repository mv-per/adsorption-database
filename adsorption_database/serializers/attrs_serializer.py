from typing import Any, Dict
from attr import fields

from h5py import Group

from adsorption_database.serializers.abstract_serializer import (
    AbstractSerializer,
)
from adsorption_database.shared import get_attr_fields_from_infos


class AttrOnlySerializer(AbstractSerializer):
    def __init__(self, model_class) -> None:
        super().__init__(model_class)

    def get_attributes(self):
        return [
            (field.name, field.type) for field in fields(self._model_class)
        ]

    def get_datasets(self):
        return []

    def load(self, group: Group) -> Any:

        attribute_infos = self.get_attributes()

        _fields: Dict[str, Any] = {}
        get_attr_fields_from_infos(_fields, attribute_infos, group)

        obj = self._model_class(**_fields)

        return obj

    def dump(self, obj: Any, group: Group) -> None:

        attributes = self.get_attributes()

        attributes_names = [attribute[0] for attribute in attributes]

        self._register_attributes(attributes_names, obj, group)
