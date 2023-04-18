from typing import Any, List, Optional
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.adsorbent import Adsorbent
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.experiment_serializer import (
    ExperimentSerializer,
)
from adsorption_database.storage_provider import StorageProvider
from adsorption_database.defaults import EXPERIMENTS, ADSORBATES, ADSORBENTS, MIXTURE_ISOTHERMS, MONO_ISOTHERMS
from adsorption_database.models.experiment import Experiment
from h5py import Group


class GroupNotFound(Exception):
    """"""


class AdsorptionDatabase:
    """
    The AdsorptionDatabase class provides methods to access and retrieve adsorption data from the adsorption database.
    """
    
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

    def _get_attr_only_obj(
        self, name: str, parent_group_name: str, model_class: Any
    ) -> Optional[Any]:

        with self._provider.get_readable_file() as f:
            obj_group = f[parent_group_name].get(name)

            if obj_group is None:
                raise GroupNotFound(f"{model_class.__name__} {name} not found")

            obj = AttrOnlySerializer(model_class).load(obj_group)

        return obj

    def list_pure_isotherms(self, experiment_name:str)->List[str]:
        self._list_group_childs(f"{EXPERIMENTS}/{experiment_name}/{MONO_ISOTHERMS}")

    def list_mixture_isotherms(self, experiment_name:str)->List[str]:
        self._list_group_childs(f"{EXPERIMENTS}/{experiment_name}/{MIXTURE_ISOTHERMS}")

    def list_experiments(self) -> List[str]:
        """
        Retrieve the unique experiments present in the adsorption database as a list of strings.

        :return: The unique experiments as a list of strings.
        :rtype: List[str]
        """
        return self._list_group_childs(EXPERIMENTS)

    def list_adsorbates(self) -> List[str]:
        """
        Retrieve the unique adsorbate species present in the adsorption database as a list of strings.

        :return: The unique adsorbate species as a list of strings.
        :rtype: List[str]

        """
        return self._list_group_childs(ADSORBATES)

    def list_adsorbents(self) -> List[str]:
        """
        Retrieve the unique adsorbent materials present in the adsorption database as a list of strings.

        :return: The unique adsorbent materials as a list of strings.
        :rtype: List[str]
        """
        return self._list_group_childs(ADSORBENTS)

    def get_experiment(self, experiment_name: str) -> Optional[Experiment]:
        """
        Retrieve an experiment with the given name from the adsorption database.

        This method reads the experiment data from the adsorption database and returns an instance of the `Experiment`
        class, which represents the experiment data.

        :param experiment_name: The name of the experiment to retrieve.
        :type experiment_name: str
        :return: An instance of the `Experiment` class representing the retrieved experiment data, or None if the experiment
                 with the given name is not found.
        :rtype: Optional[Experiment]
        :raises GroupNotFound: If the experiment with the given name is not found in the adsorption database.
        """

        with self._provider.get_readable_file() as f:
            experiment_group = f[EXPERIMENTS].get(experiment_name)

            if experiment_group is None:
                raise GroupNotFound(f"Experiment {experiment_name} not found")

            experiment = ExperimentSerializer().load(experiment_group)

        return experiment

    def get_adsorbate(self, name: str) -> Optional[Adsorbate]:
        """
        Retrieve an adsorbate with the given name from the adsorption database.

        This method reads the adsorbate data from the adsorption database and returns an instance of the `Adsorbate`
        class, which represents the adsorbate data.

        :param name: The name of the adsorbate to retrieve.
        :type name: str
        :return: An instance of the `Adsorbate` class representing the retrieved adsorbate data, or None if the adsorbate
                 with the given name is not found.
        :rtype: Optional[Adsorbate]
        """
        return self._get_attr_only_obj(name, ADSORBATES, Adsorbate)

    def get_adsorbent(self, name: str) -> Optional[Adsorbent]:
        """
        Retrieve an adsorbent with the given name from the adsorption database.

        This method reads the adsorbent data from the adsorption database and returns an instance of the `Adsorbent`
        class, which represents the adsorbent data.

        :param name: The name of the adsorbent to retrieve.
        :type name: str
        :return: An instance of the `Adsorbent` class representing the retrieved adsorbent data, or None if the adsorbent
                 with the given name is not found.
        :rtype: Optional[Adsorbent]
        """
        return self._get_attr_only_obj(name, ADSORBENTS, Adsorbent)
