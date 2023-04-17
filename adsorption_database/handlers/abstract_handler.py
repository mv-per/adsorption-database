from abc import abstractmethod
from typing import Generic, Optional, Tuple, TypeVar
from h5py import Group
import numpy as np
import numpy.typing as npt
from adsorption_database.defaults import (
    ADSORBATES,
    ADSORBENTS,
)

from adsorption_database.models.adsorbent import Adsorbent
from adsorption_database.models.experiment import Experiment
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.isotherms import (
    MixIsothermFileData,
    MonoIsothermFileData,
    MixIsotherm,
    MonoIsotherm,
    IsothermType,
)
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.experiment_serializer import (
    ExperimentSerializer,
)
from adsorption_database.serializers.mix_isotherm_serializer import (
    MixIsothermSerializer,
)
from adsorption_database.serializers.mono_isotherm_serializer import (
    MonoIsothermSerializer,
)
from adsorption_database.shared import (
    get_experiments_group,
    get_isotherm_store_name,
    get_mix_isotherm_group,
    get_mono_isotherm_group,
)

from adsorption_database.storage_provider import StorageProvider


_MonoFileData = TypeVar("_MonoFileData", bound=MonoIsothermFileData)
_MixFileData = TypeVar("_MixFileData", bound=MixIsothermFileData)


class AbstractHandler(Generic[_MonoFileData, _MixFileData]):
    def __init__(self) -> None:
        self._storage_provider = StorageProvider()

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
            adsorbates_group = file.require_group(ADSORBATES)
            group = adsorbates_group.require_group(adsorbate.name)
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
            adsorbents_group = file.require_group(ADSORBENTS)
            group = adsorbents_group.require_group(adsorbent.name)
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

            experiments_group = get_experiments_group(file)
            group = experiments_group.require_group(experiment.name)

            self.register_adsorbent(experiment.adsorbent)

            # register isotherms
            isotherm_names = []
            for pure_isotherm in experiment.monocomponent_isotherms:
                isotherm_names.append(
                    self.register_mono_isotherm(pure_isotherm, group)
                )

            isotherm_names = []
            for mix_isotherm in experiment.mixture_isotherms:
                isotherm_names.append(
                    self.register_mix_isotherm(mix_isotherm, group)
                )

            ExperimentSerializer().dump(experiment, group)

    def register_mono_isotherm(
        self, isotherm: MonoIsotherm, experiment_group: Group
    ):
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

        pure_isotherms_group = get_mono_isotherm_group(experiment_group)
        stored_isotherm_name = get_isotherm_store_name(isotherm)

        self.register_adsorbate(isotherm.adsorbate)

        isotherm_group = pure_isotherms_group.require_group(
            stored_isotherm_name
        )

        MonoIsothermSerializer().dump(isotherm, isotherm_group)
        return stored_isotherm_name

    def register_mix_isotherm(
        self, isotherm: MixIsotherm, experiment_group: Group
    ):
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

        mixture_isotherms_group = get_mix_isotherm_group(experiment_group)
        stored_isotherm_name = get_isotherm_store_name(isotherm)

        for adsorbate in isotherm.adsorbates:
            self.register_adsorbate(adsorbate)

        isotherm_group = mixture_isotherms_group.require_group(
            stored_isotherm_name
        )

        MixIsothermSerializer().dump(isotherm, isotherm_group)

        return stored_isotherm_name

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
    ) -> Tuple[
        npt.NDArray[np.float64],
        npt.NDArray[np.float64],
        npt.NDArray[np.float64],
    ]:
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
