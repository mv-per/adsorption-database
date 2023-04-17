from pathlib import Path

import pytest
from adsorption_database.defaults import (
    ADSORBATES,
    EXPERIMENTS,
    MONO_ISOTHERMS,
)
from adsorption_database.helpers import Helpers
from pytest_regressions.data_regression import DataRegressionFixture
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.isotherms import MonoIsotherm
from adsorption_database.serializers.abstract_serializer import (
    AbstractSerializer,
)
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.mono_isotherm_serializer import (
    MonoIsothermSerializer,
)
from adsorption_database.storage_provider import StorageProvider
from pytest_lazyfixture import lazy_fixture
from h5py import Group


def setup_file(
    serializer: AbstractSerializer,
    co2_adsorbate: Adsorbate,
    isotherm: MonoIsotherm,
    f: Group,
) -> None:
    adsorbates = f.create_group(ADSORBATES)
    co2_group = adsorbates.create_group(co2_adsorbate.name)
    AttrOnlySerializer(Adsorbate).dump(co2_adsorbate, co2_group)

    f.create_group(EXPERIMENTS)
    experiment_group = f[EXPERIMENTS].create_group("A")
    mono_isotherms = experiment_group.create_group(MONO_ISOTHERMS)
    isotherm_group = mono_isotherms.create_group(isotherm.name)
    serializer.dump(isotherm, isotherm_group)


@pytest.mark.parametrize(
    "isotherm",
    [
        lazy_fixture("mono_isotherm"),
        lazy_fixture("mono_isotherm_with_heats_of_adsorption"),
    ],
)
def test_dump_mono_isotherm(
    isotherm: MonoIsotherm,
    co2_adsorbate: Adsorbate,
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:

    serializer = MonoIsothermSerializer()

    with StorageProvider().get_editable_file() as f:
        setup_file(serializer, co2_adsorbate, isotherm, f)

    serialized_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": serialized_tree})


@pytest.mark.parametrize(
    "isotherm",
    [
        lazy_fixture("mono_isotherm"),
        lazy_fixture("mono_isotherm_with_heats_of_adsorption"),
    ],
)
def test_load_mono_isotherm(
    isotherm: MonoIsotherm, co2_adsorbate: Adsorbate, helpers: Helpers
) -> None:
    serializer = MonoIsothermSerializer()

    with StorageProvider().get_editable_file() as f:
        setup_file(serializer, co2_adsorbate, isotherm, f)

    with StorageProvider().get_readable_file() as f:
        obj = serializer.load(
            f[EXPERIMENTS]["A"][MONO_ISOTHERMS][isotherm.name]
        )

    helpers.assert_equal(isotherm, obj)
