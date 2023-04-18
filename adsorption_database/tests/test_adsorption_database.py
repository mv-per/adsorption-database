from adsorption_database import AdsorptionDatabase
from pytest_regressions.data_regression import DataRegressionFixture
from adsorption_database.helpers import Helpers


def test_list_experiments(data_regression: DataRegressionFixture) -> None:

    database = AdsorptionDatabase()

    experiments = database.list_experiments()

    data_regression.check({"experiments": experiments})

def test_list_papers(data_regression: DataRegressionFixture) -> None:

    database = AdsorptionDatabase()

    experiments = database.list_experiments()

    paper_ulrs = []
    for experiment in experiments:
        exp = database.get_experiment(experiment)
        if exp is None:
            continue
        paper_ulrs.append(exp.paper_url)

    data_regression.check({"papers": paper_ulrs})


def test_list_adsorbates(data_regression: DataRegressionFixture) -> None:

    database = AdsorptionDatabase()

    adsorbates = database.list_adsorbates()

    data_regression.check({"adsorbates": adsorbates})


def test_list_adsorbents(data_regression: DataRegressionFixture) -> None:

    database = AdsorptionDatabase()

    adsorbents = database.list_adsorbents()

    data_regression.check({"adsorbents": adsorbents})


def test_get_experiment() -> None:

    database = AdsorptionDatabase()

    experiment = database.get_experiment("Dre-norit-R1")

    assert experiment


def test_get_adsobate() -> None:

    database = AdsorptionDatabase()

    adsorbates = database.list_adsorbates()

    adsorbate = database.get_adsorbate(adsorbates[0])
    assert adsorbate is not None
    assert adsorbate.name is not None
    assert adsorbate.chemical_formula is not None


def test_get_adsobent() -> None:

    database = AdsorptionDatabase()

    adsorbents = database.list_adsorbents()

    adsorbent = database.get_adsorbent(adsorbents[0])
    assert adsorbent is not None
    assert adsorbent.name is not None
    assert adsorbent.type is not None


def test_get_storage_regression(
    helpers: Helpers, data_regression: DataRegressionFixture
) -> None:

    from adsorption_database.storage_provider import StorageProvider

    path = StorageProvider().get_file_path()

    serialized_tree = helpers.dump_storage_tree(path)

    data_regression.check({"tree": serialized_tree})
