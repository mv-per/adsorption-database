import enum
from typing import Any, List
from h5py import Group
from abc import abstractmethod
import numpy.typing as npt
from abc import abstractmethod


class AbstractSerializer:
    def __init__(self, model_class) -> None:
        self._model_class = model_class

    @abstractmethod
    def get_attributes(self):
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_datasets(self):
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_softlinks_route(self):
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def load(self, group: Group) -> Any:
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def dump(self, obj: Any, group: Group) -> None:
        raise NotImplementedError()  # pragma: no cover

    def _register_attributes(self, fields: List[str], object: Any, group: Group) -> None:

        for field in fields:
            val = getattr(object, field)
            if val is None:
                continue
            if isinstance(val, enum.Enum):
                val = val.value
            group.attrs.create(field, val)

    def _register_datasets(self, dataset_names: List[str], object: Any, group: Group) -> None:

        for dataset_name in dataset_names:
            val = getattr(object, dataset_name)
            if val is None:
                continue
            self.upsert_dataset(group, dataset_name, val)

    def upsert_dataset(self, group: Group, dataset_name: str, values: npt.NDArray) -> None:
        """
        Upsert a dataset in a HDF5 group.

        This method checks if a dataset with the given `dataset_name` already exists in the `group`. If it does, it
        is deleted and a new dataset with the same name is created with the provided `values`. If it does not exist,
        a new dataset with the given `dataset_name` is created with the provided `values`.

        Args:
            group (h5py.Group): The HDF5 group where the dataset will be upserted.
            dataset_name (str): The name of the dataset to be upserted.
            values (np.ndarray): The data to be stored in the dataset.

        Returns:
            None

        Raises:
            KeyError: If `dataset_name` is not a valid string.
        """

        dataset = group.get(dataset_name)

        if dataset is not None:
            del group[dataset_name]

        group.create_dataset(dataset_name, data=values)
