from pathlib import Path
from adsorption_database.helpers import Helpers
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.adsorbent import Adsorbent, AdsorbentType
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from pytest_regressions.data_regression import DataRegressionFixture

from adsorption_database.storage_provider import StorageProvider


def test_dump_adsorbate(
    co2_adsorbate: Adsorbate,
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:
    serializer = AttrOnlySerializer(Adsorbate)

    with StorageProvider().get_editable_file() as f:
        serializer.dump(co2_adsorbate, f)

    serialized_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": serialized_tree})


def test_load_adsorbate(co2_adsorbate: Adsorbate, helpers: Helpers) -> None:
    serializer = AttrOnlySerializer(Adsorbate)

    with StorageProvider().get_editable_file() as f:
        serializer.dump(co2_adsorbate, f)

    with StorageProvider().get_readable_file() as f:
        adsorbate_obj = serializer.load(f)

    helpers.assert_equal(co2_adsorbate, adsorbate_obj)


def test_dump_adsorbent(
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:

    mock_adsorbent = Adsorbent(AdsorbentType.ZEOLITE, "z01x", 100, 20)

    serializer = AttrOnlySerializer(Adsorbent)

    with StorageProvider().get_editable_file() as f:
        serializer.dump(mock_adsorbent, f)

    serialized_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": serialized_tree})


def test_load_adsorbent(helpers: Helpers) -> None:

    mock_adsorbent = Adsorbent(AdsorbentType.ZEOLITE, "z01x", 100, 20)

    serializer = AttrOnlySerializer(Adsorbent)

    with StorageProvider().get_editable_file() as f:
        serializer.dump(mock_adsorbent, f)

    with StorageProvider().get_readable_file() as f:
        obj = serializer.load(f)

    helpers.assert_equal(mock_adsorbent, obj)
