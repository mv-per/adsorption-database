from typing import Any, List, Optional
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.adsorbent import Adsorbent
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.experiment_serializer import (
    ExperimentSerializer,
)
from adsorption_database.storage_provider import StorageProvider
from adsorption_database.defaults import EXPERIMENTS, ADSORBATES, ADSORBENTS
from adsorption_database.models.experiment import Experiment
from h5py import Group


class GroupNotFound(Exception):
    """"""


class AdsorptionDatabase:
    def __init__(self):
        self._provider = StorageProvider()

    def _list_group_childs(
        self, child_name: str, parent_group: Optional[Group] = None
    ) -> List[str]:

        if parent_group is not None:
            return list(parent_group[child_name])

        with self._provider.get_readable_file() as f:
            childs = list(f[child_name])
        return childs

    def get_attr_only_obj(
        self, name: str, parent_group_name: str, model_class: Any
    ) -> Optional[Any]:

        with self._provider.get_readable_file() as f:
            obj_group = f[parent_group_name].get(name)

            if obj_group is None:
                raise GroupNotFound(f"{model_class.__name__} {name} not found")

            obj = AttrOnlySerializer(model_class).load(obj_group)

        return obj

    def list_experiments(self) -> List[str]:
        return self._list_group_childs(EXPERIMENTS)

    def list_adsorbates(self) -> List[str]:
        return self._list_group_childs(ADSORBATES)

    def list_adsorbents(self) -> List[str]:
        return self._list_group_childs(ADSORBENTS)

    def get_experiment(self, experiment_name: str) -> Optional[Experiment]:

        with self._provider.get_readable_file() as f:
            experiment_group = f[EXPERIMENTS].get(experiment_name)

            if experiment_group is None:
                raise GroupNotFound(f"Experiment {experiment_name} not found")

            experiment = ExperimentSerializer().load(experiment_group)

        return experiment

    def get_adsorbate(self, name: str) -> Optional[Adsorbate]:
        return self.get_attr_only_obj(name, ADSORBATES, Adsorbate)

    def get_adsorbent(self, name: str) -> Optional[Adsorbent]:
        return self.get_attr_only_obj(name, ADSORBENTS, Adsorbent)
