from abc import abstractmethod
from attrs import fields
from typing import Generic, Optional, Tuple, TypeVar, Union, List, Any
import enum
from h5py import File, Group, SoftLink
import numpy as np
import numpy.typing as npt
from adsorption_database.defaults import (
    ADSORBATES,
    ADSORBENTS,
    EXPERIMENTS,
    MIXTURE_ISOTHERMS,
    MONO_ISOTHERMS,
    SEPARATOR,
)
from adsorption_database.helpers import Helpers


from adsorption_database.models import (
    MixIsotherm,
    MonoIsotherm,
    IsothermType,
    Adsorbate,
    Experiment,
)
from adsorption_database.models.adsorbent import Adsorbent
from adsorption_database.models.isotherms import MixIsothermFileData, MonoIsothermFileData
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.experiment_serializer import ExperimentSerializer
from adsorption_database.serializers.mix_isotherm_serializer import MixIsothermSerializer
from adsorption_database.serializers.mono_isotherm_serializer import MonoIsothermSerializer

from adsorption_database.storage_provider import StorageProvider


_MonoFileData = TypeVar("_MonoFileData", bound=MonoIsothermFileData)
_MixFileData = TypeVar("_MixFileData", bound=MixIsothermFileData)


class AbstractHandler(Generic[_MonoFileData, _MixFileData]):
    def __init__(self) -> None:
        self._storage_provider = StorageProvider()

    def get_group(self, group_name: str, parent_group: Group) -> Group:
        """
        Get or create a group within a parent group in an HDF5 file.

        This method searches for a group with the given `group_name` within the `parent_group`. If the group does
        not exist, a new group with the given `group_name` is created within the `parent_group`.

        Args:
            group_name (str): The name of the group to get or create.
            parent_group (h5py.Group): The parent group where the group will be searched for or created.

        Returns:
            h5py.Group: The group object with the given `group_name`.
        """

        group = parent_group.get(group_name)

        if group is None:
            group = parent_group.create_group(group_name)

        return group

    def get_mono_isotherm_group(self, experiment_group: Group) -> Group:
        """
        Get the group object for storing pure component isotherm data.

        This method retrieves the HDF5 group object for storing pure component isotherm data within an experiment
        group. The group object is retrieved based on a predefined group name.

        Args:
            experiment_group (Group): The experiment group object within which to get the pure component isotherm group.

        Returns:
            Group: The group object for storing pure component isotherm data.
        """
        return self.get_group(MONO_ISOTHERMS, experiment_group)

    def get_experiment_group(self, file: File) -> Group:
        """
        Get the group object for storing pure component isotherm data.

        This method retrieves the HDF5 group object for storing pure component isotherm data within an experiment
        group. The group object is retrieved based on a predefined group name.

        Args:
            experiment_group (Group): The experiment group object within which to get the pure component isotherm group.

        Returns:
            Group: The group object for storing pure component isotherm data.
        """
        return self.get_group(EXPERIMENTS, file)

    def get_mix_isotherm_group(self, experiment_group: Group) -> Group:
        """
        Get the group object for storing mixture isotherm data.

        This method retrieves the HDF5 group object for storing mixture isotherm data within an experiment
        group. The group object is retrieved based on a predefined group name.

        Args:
            experiment_group (Group): The experiment group object within which to get the mixture isotherm group.

        Returns:
            Group: The group object for storing mixture isotherm data.
        """
        return self.get_group(MIXTURE_ISOTHERMS, experiment_group)

    def get_isotherm_store_name(self, isotherm: Union[MixIsotherm, MonoIsotherm]) -> str:
        """
        Get the store name for an isotherm object.

        This method generates a unique store name for an isotherm object based on its name and type. The
        generated store name is a string combining the isotherm's name and type with a hyphen separator.

        Args:
            isotherm (Union[MixIsotherm, MonoIsotherm]): The isotherm object for which to generate the store name.

        Returns:
            str: The generated store name.
        """
        return f"{isotherm.name}-{isotherm.isotherm_type.value}"

    def register_adsorbate(self, adsorbate: Adsorbate) -> None:
        """
        Register an adsorbate in the HDF5 file.

        This method registers an `Adsorbate` object in the HDF5 file, storing its information as attributes
        in a group within the 'adsorbates' group in the file. The group is created if it does not already exist.

        Args:
            adsorbate (Adsorbate): The adsorbate object to register.

        Returns:
            None
        """

        with self._storage_provider.get_editable_file() as file:
            adsorbates_group = self.get_group(ADSORBATES, file)
            group = self.get_group(adsorbate.name, adsorbates_group)
            AttrOnlySerializer(Adsorbate).dump(adsorbate, group)

    def register_adsorbent(self, adsorbent: Adsorbent) -> None:
        """
        Register an Adsorbent in the HDF5 file.

        This method registers an `Adsorbent` object in the HDF5 file, storing its information as attributes
        in a group within the 'Adsorbents' group in the file. The group is created if it does not already exist.

        Args:
            adsorbent (Adsorbent): The Adsorbent object to register.

        Returns:
            None
        """

        with self._storage_provider.get_editable_file() as file:
            adsorbents_group = self.get_group(ADSORBENTS, file)
            group = self.get_group(adsorbent.name, adsorbents_group)
            AttrOnlySerializer(Adsorbent).dump(adsorbent, group)

    def register_experiment(self, experiment: Experiment):
        """
        Register an experiment and associated data in the HDF5 file.

        This method registers an experiment object and associated data, including attributes and datasets,
        in the HDF5 file. The experiment data is stored in an experiment group within the HDF5 file.

        Args:
            experiment (Experiment): The experiment object to be registered in the HDF5 file.

        Returns:
            None
        """

        with self._storage_provider.get_editable_file() as file:

            experiments_group = self.get_experiment_group(file)
            group = self.get_group(experiment.name, experiments_group)

            ExperimentSerializer().dump(experiment, group)

            # register datasets
            isotherm_names = []
            for pure_isotherm in experiment.monocomponent_isotherms:
                isotherm_names.append(self.register_mono_isotherm(pure_isotherm, group))
            group.attrs.create("monocomponent_isotherms", SEPARATOR.join(isotherm_names))

            isotherm_names = []
            for mix_isotherm in experiment.mixture_isotherms:
                isotherm_names.append(self.register_mix_isotherm(mix_isotherm, group))
            group.attrs.create("mixture_isotherms", SEPARATOR.join(isotherm_names))

    def register_mono_isotherm(self, isotherm: MonoIsotherm, experiment_group: Group):
        """
        Register a monocomponent isotherm and associated data in the HDF5 file.

        This method registers a monocomponent isotherm object and associated data, including attributes and
        datasets, in the HDF5 file. The monocomponent isotherm data is stored in a group within the experiment
        group in the HDF5 file.

        Args:
            isotherm (MonoIsotherm): The monocomponent isotherm object to be registered in the HDF5 file.
            experiment_group (Group): The experiment group to which the monocomponent isotherm belongs.

        Returns:
            None
        """

        pure_isotherms_group = self.get_mono_isotherm_group(experiment_group)
        stored_isotherm_name = self.get_isotherm_store_name(isotherm)

        isotherm_group = self.get_group(stored_isotherm_name, pure_isotherms_group)

        MonoIsothermSerializer().dump(isotherm, isotherm_group)
        return stored_isotherm_name

    def register_mix_isotherm(self, isotherm: MixIsotherm, experiment_group: Group):
        """
        Register a multicomponent isotherm and associated data in the HDF5 file.

        This method registers a multicomponent isotherm object and associated data, including attributes and
        datasets, in the HDF5 file. The multicomponent isotherm data is stored in a group within the experiment
        group in the HDF5 file.

        Args:
            isotherm (MixIsotherm): The multicomponent isotherm object to be registered in the HDF5 file.
            experiment_group (Group): The experiment group to which the multicomponent isotherm belongs.

        Returns:
            None
        """

        mixture_isotherms_group = self.get_mix_isotherm_group(experiment_group)
        stored_isotherm_name = self.get_isotherm_store_name(isotherm)

        isotherm_group = self.get_group(stored_isotherm_name, mixture_isotherms_group)

        MixIsothermSerializer().dump(isotherm, isotherm_group)

        return stored_isotherm_name

    def gen_regression(self) -> None:
        import json

        path = self._storage_provider.get_file_path()
        regression = Helpers().dump_storage_tree(path)

        data = {"data": regression}
        with open(path.parent.resolve() / "storage_regression.json", "w") as f:
            json.dump(data, f)

    @abstractmethod
    def get_mono_data(
        self, file_data: _MonoFileData
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """
        Get monocomponent isotherm data from file data.

        This method retrieves monocomponent isotherm data, including pressures and loadings, from the provided
        file data.

        Args:
            file_data (_MonoFileData): The file data containing adsorbate, pressures, and loadings for extracting pressure and loadings data

        Returns:
            Tuple[List[float], List[float]]: A tuple containing two lists - pressures and loadings
        """
        raise NotImplementedError()

    def create_mono_isotherm(
        self,
        name: str,
        temperature: float,
        isotherm_type: IsothermType,
        file_data: _MonoFileData,
        heats_of_adsorption: Optional[npt.NDArray[np.float64]] = None,
        comments: Optional[str] = None,
    ) -> MonoIsotherm:
        """
        Create a monocomponent isotherm object from file data.

        This method creates a monocomponent isotherm object with the specified name, isotherm type, adsorbate,
        pressures, heats of adsorption, loadings, and comments, using the provided file data. The file data is
        extracted to obtain pressures and loadings for the monocomponent isotherm.

        Args:
            name (str): The name of the monocomponent isotherm.
            isotherm_type (IsothermType): The type of the monocomponent isotherm, defined by an enum value from IsothermType.
            file_data (_MonoFileData): The file data containing adsorbate, pressures, and loadings for the monocomponent isotherm.
            heats_of_adsorption (Optional[str], optional): The heats of adsorption data for the monocomponent isotherm. Defaults to None.
            comments (Optional[str], optional): Comments or additional information about the monocomponent isotherm. Defaults to None.

        Returns:
            MonoIsotherm: The monocomponent isotherm object created from the file data.

        Raises:
            None
        """
        pressures, loadings = self.get_mono_data(file_data)

        return MonoIsotherm(
            name=name,
            isotherm_type=isotherm_type,
            adsorbate=file_data.adsorbate,
            pressures=pressures,
            heats_of_adsorption=heats_of_adsorption,
            loadings=loadings,
            comments=comments,
            temperature=temperature,
        )

    @abstractmethod
    def get_mix_data(
        self,
        file_data: _MixFileData,
    ) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], npt.NDArray[np.float64]]:
        """
        Get mixed-component isotherm data from file data.

        This method retrieves mixed-component isotherm data, including pressures, loadings, and bulk
        composition, from the provided file data.

        Args:
            file_data (_MixFileData): The file data for the mixed-component isotherm.

        Returns:
            Tuple[List[float], List[List[float]], List[List[float]]]: A tuple containing three lists -
            pressures, loadings, and bulk composition.
        """
        raise NotImplementedError()

    def create_mix_isotherm(
        self,
        name: str,
        temperature: float,
        isotherm_type: IsothermType,
        file_data: _MixFileData,
        comments: Optional[str] = None,
    ) -> MixIsotherm:
        """
        Create a mixed-component isotherm object.

        This method creates a mixed-component isotherm object using the provided name, isotherm type, file data,
        and comments (optional). The created mixed-component isotherm object can be used to register isotherms in
        an HDF5 file.

        Args:
            name (str): The name of the mixed-component isotherm.
            isotherm_type (IsothermType): The type of the mixed-component isotherm.
            file_data (MixIsothermFileData): The file data for the mixed-component isotherm.
            comments (Optional[str], optional): Any comments associated with the mixed-component isotherm.
                Defaults to None.

        Returns:
            MixIsotherm: The mixed-component isotherm object.
        """
        pressures, loadings, bulk_composition = self.get_mix_data(file_data)

        return MixIsotherm(
            name=name,
            isotherm_type=isotherm_type,
            adsorbates=file_data.adsorbates,
            pressures=pressures,
            loadings=loadings,
            bulk_composition=bulk_composition,
            comments=comments,
            temperature=temperature,
        )
