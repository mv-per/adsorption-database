from pathlib import Path
from adsorption_database.defaults import ADSORBATES, EXPERIMENTS, MONO_ISOTHERMS
from adsorption_database.helpers import Helpers
from pytest_regressions.data_regression import DataRegressionFixture
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.isotherms import MonoIsotherm
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.mono_isotherm_serializer import MonoIsothermSerializer
from adsorption_database.serializers.shared import assert_equal
from adsorption_database.storage_provider import StorageProvider


def test_dump_mono_isotherm(
    mono_isotherm: MonoIsotherm,
    co2_adsorbate: Adsorbate,
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:

    serializer = MonoIsothermSerializer()

    with StorageProvider().get_editable_file() as f:
        f.create_group(EXPERIMENTS)
        adsorbates = f.create_group(ADSORBATES)
        co2_group = adsorbates.create_group(co2_adsorbate.name)
        experiment_group = f[EXPERIMENTS].create_group("A")
        mono_isotherms = experiment_group.create_group(MONO_ISOTHERMS)

        mono_isotherms.create_group("isotherm name")
        AttrOnlySerializer(Adsorbate).dump(co2_adsorbate, adsorbates)
        serializer.dump(mono_isotherm, mono_isotherms)

    serialized_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": serialized_tree})


def test_load_mono_isotherm(
    mono_isotherm: MonoIsotherm,
    co2_adsorbate: Adsorbate,
) -> None:
    serializer = MonoIsothermSerializer()

    with StorageProvider().get_editable_file() as f:
        f.create_group(EXPERIMENTS)
        adsorbates = f.create_group(ADSORBATES)
        co2_group = adsorbates.create_group(co2_adsorbate.name)
        experiment_group = f[EXPERIMENTS].create_group("A")
        mono_isotherms = experiment_group.create_group(MONO_ISOTHERMS)

        isotherm_group = mono_isotherms.create_group(mono_isotherm.name)
        AttrOnlySerializer(Adsorbate).dump(co2_adsorbate, co2_group)
        serializer.dump(mono_isotherm, isotherm_group)

    with StorageProvider().get_readable_file() as f:
        obj = serializer.load(f[EXPERIMENTS]["A"][MONO_ISOTHERMS][mono_isotherm.name])

    assert_equal(mono_isotherm, obj)
