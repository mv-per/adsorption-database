from pathlib import Path

import pytest
from adsorption_database.defaults import (
    ADSORBATES,
    EXPERIMENTS,
    MIXTURE_ISOTHERMS,
)
from adsorption_database.helpers import Helpers
from pytest_regressions.data_regression import DataRegressionFixture
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.isotherms import MixIsotherm
from adsorption_database.serializers.abstract_serializer import (
    AbstractSerializer,
)
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.mix_isotherm_serializer import (
    MixIsothermSerializer,
)
from adsorption_database.storage_provider import StorageProvider
from h5py import Group


@pytest.fixture
def setup_test_storage(
    co2_adsorbate: Adsorbate,
    ch4_adsorbate: Adsorbate,
    mix_isotherm: MixIsotherm,
) -> None:
    serializer = MixIsothermSerializer()
    with StorageProvider().get_editable_file() as f:
        isotherm_group = f.create_group(
            EXPERIMENTS
            + "/"
            + "A"
            + "/"
            + MIXTURE_ISOTHERMS
            + "/"
            + mix_isotherm.name
        )
        adsorbates = f.create_group(ADSORBATES)
        co2_group = adsorbates.create_group(co2_adsorbate.name)
        ch4_group = adsorbates.create_group(ch4_adsorbate.name)
        AttrOnlySerializer(Adsorbate).dump(co2_adsorbate, co2_group)
        AttrOnlySerializer(Adsorbate).dump(ch4_adsorbate, ch4_group)

        serializer.dump(mix_isotherm, isotherm_group)


def test_dump_mix_isotherm(
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
    setup_test_storage: None,
) -> None:

    serialized_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": serialized_tree})


def test_load_mix_isotherm(
    setup_test_storage: None, mix_isotherm: MixIsotherm, helpers: Helpers
) -> None:
    serializer = MixIsothermSerializer()

    with StorageProvider().get_readable_file() as f:
        obj = serializer.load(
            f[EXPERIMENTS]["A"][MIXTURE_ISOTHERMS][mix_isotherm.name]
        )

    helpers.assert_equal(mix_isotherm, obj)
