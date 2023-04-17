from typing import List, Optional
from adsorption_database.serializers.experiment_serializer import ExperimentSerializer
from adsorption_database.storage_provider import StorageProvider
from adsorption_database.defaults import EXPERIMENTS, ADSORBATES, ADSORBENTS
from adsorption_database.models.experiment import Experiment
from h5py import Group


class ExperimentNotFound(Exception):
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
                raise ExperimentNotFound(f"Experiment {experiment_name} not found")

            experiment = ExperimentSerializer().load(experiment_group)

        return experiment
