from typing import Any
from attr import define
import numpy as np
import pytest
from h5py import Group
from adsorption_database.serializers.abstract_serializer import AbstractSerializer
from adsorption_database.storage_provider import StorageProvider


@define
class MockClass:
    name: str


class Serializer(AbstractSerializer):
    def dump(self, obj: Any, group: Group) -> None:
        return super().dump(obj, group)

    def load(self, group: Group) -> Any:
        return super().load(group)

    def get_attributes(self):
        return super().get_attributes()

    def get_datasets(self):
        return super().get_datasets()


def test_upsert_dataset() -> None:

    serializer = Serializer(MockClass)

    dataset_name = "my_dataset"
    with StorageProvider().get_editable_file() as f:
        assert dataset_name not in list(f)

        # Test creating dataset
        dataset_values = np.array([1, 2, 3, 4, 5, 6, 7], dtype="float64")
        serializer.upsert_dataset(f, dataset_name, dataset_values)
        assert (np.array(f[dataset_name]) == dataset_values).all()

        # Test updating dataset to a different shape
        dataset_values = np.array([8, 9, 10, 11, 12], dtype="float64")
        serializer.upsert_dataset(f, dataset_name, dataset_values)
        assert (np.array(f[dataset_name]) == dataset_values).all()

        # Test updating dataset to a different shape increazing column
        a = np.array([1, 2, 3, 4, 5, 6, 7], dtype="float64")
        b = np.array([8, 9, 10, 11, 12, 13, 14], dtype="float64")
        assert (
            a.shape == b.shape
        )  # Without ensuring the same length, the new dataset will have type 'O', causing an error in the upsert method
        dataset_values = np.array([a, b])

        serializer.upsert_dataset(f, dataset_name, dataset_values)
        assert (np.array(f[dataset_name]) == dataset_values).all()


def test_upsert_dataset_type_o_error() -> None:

    serializer = Serializer(MockClass)

    dataset_name = "my_dataset"

    with StorageProvider().get_editable_file() as f:
        a = np.array([1, 2, 3, 4, 5, 6, 7], dtype="float64")
        b = np.array([4, 5, 6], dtype="float64")
        dataset_values = np.array([a, b], dtype=object)

        with pytest.raises(TypeError) as exc_info:
            serializer.upsert_dataset(f, dataset_name, dataset_values)

        assert str(exc_info.value) == "Object dtype dtype('O') has no native HDF5 equivalent"
