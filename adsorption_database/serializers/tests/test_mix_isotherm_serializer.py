from pathlib import Path
from adsorption_database.defaults import ADSORBATES, EXPERIMENTS, MIXTURE_ISOTHERMS
from adsorption_database.helpers import Helpers
from pytest_regressions.data_regression import DataRegressionFixture
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.isotherms import MixIsotherm
from adsorption_database.serializers.attrs_serializer import AttrOnlySerializer
from adsorption_database.serializers.mix_isotherm_serializer import MixIsothermSerializer
from adsorption_database.serializers.shared import assert_equal
from adsorption_database.storage_provider import StorageProvider


def test_dump_mix_isotherm(
    mix_isotherm: MixIsotherm,
    co2_adsorbate: Adsorbate,
    ch4_adsorbate: Adsorbate,
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:

    serializer = MixIsothermSerializer()

    with StorageProvider().get_editable_file() as f:
        f.create_group(EXPERIMENTS)
        adsorbates = f.create_group(ADSORBATES)
        co2_group = adsorbates.create_group(co2_adsorbate.name)
        ch4_group = adsorbates.create_group(ch4_adsorbate.name)
        AttrOnlySerializer(Adsorbate).dump(co2_adsorbate, co2_group)
        AttrOnlySerializer(Adsorbate).dump(ch4_adsorbate, ch4_group)

        experiment_group = f[EXPERIMENTS].create_group("A")
        isotherm_group = experiment_group.create_group(MIXTURE_ISOTHERMS)

        isotherm_group.create_group(mix_isotherm.name)

        serializer.dump(mix_isotherm, isotherm_group[mix_isotherm.name])

    serialized_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": serialized_tree})


def test_load_mix_isotherm(
    mix_isotherm: MixIsotherm,
    co2_adsorbate: Adsorbate,
    ch4_adsorbate: Adsorbate,
) -> None:
    serializer = MixIsothermSerializer()

    with StorageProvider().get_editable_file() as f:
        f.create_group(EXPERIMENTS)
        adsorbates = f.create_group(ADSORBATES)
        co2_group = adsorbates.create_group(co2_adsorbate.name)
        ch4_group = adsorbates.create_group(ch4_adsorbate.name)
        AttrOnlySerializer(Adsorbate).dump(co2_adsorbate, co2_group)
        AttrOnlySerializer(Adsorbate).dump(ch4_adsorbate, ch4_group)

        experiment_group = f[EXPERIMENTS].create_group("A")
        mix_isotherms = experiment_group.create_group(MIXTURE_ISOTHERMS)
        isotherm_group = mix_isotherms.create_group(mix_isotherm.name)
        serializer.dump(mix_isotherm, isotherm_group)

    with StorageProvider().get_readable_file() as f:
        obj = serializer.load(f[EXPERIMENTS]["A"][MIXTURE_ISOTHERMS][mix_isotherm.name])

    assert_equal(mix_isotherm, obj)
