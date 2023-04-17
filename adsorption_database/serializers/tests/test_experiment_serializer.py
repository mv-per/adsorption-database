from pathlib import Path

import pytest
from adsorption_database.defaults import (
    ADSORBATES,
    ADSORBENTS,
    EXPERIMENTS,
    MIXTURE_ISOTHERMS,
    MONO_ISOTHERMS,
)
from adsorption_database.helpers import Helpers
from pytest_regressions.data_regression import DataRegressionFixture
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.adsorbent import Adsorbent, AdsorbentType
from adsorption_database.models.experiment import Experiment, ExperimentType
from adsorption_database.models.isotherms import MixIsotherm, MonoIsotherm
from adsorption_database.serializers.abstract_serializer import (
    AbstractSerializer,
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
from adsorption_database.storage_provider import StorageProvider


@pytest.fixture
def setup_test_storage(
    co2_adsorbate: Adsorbate,
    ch4_adsorbate: Adsorbate,
    mix_isotherm: MixIsotherm,
    mono_isotherm: MonoIsotherm,
    setup_storage: Path,
) -> Experiment:

    serializer = ExperimentSerializer()

    with StorageProvider().get_editable_file() as f:
        adsorbates = f.create_group(ADSORBATES)
        co2_group = adsorbates.create_group(co2_adsorbate.name)
        ch4_group = adsorbates.create_group(ch4_adsorbate.name)
        AttrOnlySerializer(Adsorbate).dump(co2_adsorbate, co2_group)
        AttrOnlySerializer(Adsorbate).dump(ch4_adsorbate, ch4_group)
        adsorbates = f.create_group(ADSORBENTS)
        adsorbent = Adsorbent(AdsorbentType.ZEOLITE, "z01x")
        adsorbent_group = adsorbates.create_group(adsorbent.name, adsorbates)
        AttrOnlySerializer(Adsorbent).dump(adsorbent, adsorbent_group)

        experiment = Experiment(
            name="exp-01-02",
            adsorbent=adsorbent,
            experiment_type=ExperimentType.GRAVIMETRIC,
            monocomponent_isotherms=[mono_isotherm],
            mixture_isotherms=[mix_isotherm],
            year="1934",
            authors=["carol", "jhon", "maria"],
        )

        experiments_group = f.create_group(EXPERIMENTS)

        group = experiments_group.create_group(experiment.name)

        mono_iso = group.create_group(
            MONO_ISOTHERMS + "/" + mono_isotherm.name
        )
        MonoIsothermSerializer().dump(mono_isotherm, mono_iso)

        mix_iso = group.create_group(
            MIXTURE_ISOTHERMS + "/" + mix_isotherm.name
        )
        MixIsothermSerializer().dump(mix_isotherm, mix_iso)

        serializer.dump(experiment, group)

    return experiment


def test_dump_experiment(
    setup_test_storage: None,
    helpers: Helpers,
    setup_storage: Path,
    data_regression: DataRegressionFixture,
) -> None:

    serialized_tree = helpers.dump_storage_tree(setup_storage)

    data_regression.check({"tree": serialized_tree})


def test_load_experiment(
    helpers: Helpers, setup_test_storage: Experiment
) -> None:
    serializer = ExperimentSerializer()

    with StorageProvider().get_readable_file() as f:
        obj = serializer.load(f[EXPERIMENTS]["exp-01-02"])

    helpers.assert_equal(setup_test_storage, obj)
