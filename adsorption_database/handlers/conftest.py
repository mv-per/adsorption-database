import pytest
from pytest_mock import MockerFixture
from pathlib import Path
from adsorption_database.storage_provider import StorageProvider


@pytest.fixture(autouse=True)
def setup_storage(datadir: Path, mocker: MockerFixture) -> Path:
    storage_path = Path(datadir / "test_storage.hdf5")

    mocker.patch.object(StorageProvider, "get_file_path", return_value=storage_path)

    return storage_path
