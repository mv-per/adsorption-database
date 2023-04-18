import asyncio
from typing import Any, Dict
from adsorption_database import AdsorptionDatabase
from pytest_regressions.data_regression import DataRegressionFixture
from adsorption_database.helpers import Helpers


def test_list_experiments(data_regression: DataRegressionFixture) -> None:
    database = AdsorptionDatabase()

    experiments = database.list_experiments()

    data_regression.check({"experiments": experiments})

def get_paper_title(doi:str):
    import requests
    import json

    response = requests.get('https://api.crossref.org/works/' + doi)
    response_content = json.loads(response._content)

    title = response_content['message'].get('title', [None])
    authors = response_content['message'].get('author', [None])
    publisher = response_content['message'].get('publisher', [None])
    return title, authors, publisher


def test_list_papers(data_regression: DataRegressionFixture) -> None:
    database = AdsorptionDatabase()

    experiments = database.list_experiments()

    EXPs = {}
    for experiment in experiments:
        exp = database.get_experiment(experiment)
        if exp is None:
            continue
        
        titles = []
        authors = []
        publishers = []

        for doi in exp.paper_doi:
            _title, _authors, _publisher = get_paper_title(str(doi))

            titles.append(_title)
            authors.append(_authors)
            publishers.append(_publisher)

        pure_isotherms = database.list_pure_isotherms(experiment)
        mixture_isotherms = database.list_mixture_isotherms(experiment)

        EXPs[exp.name] = {
            "Database Experiment Name": exp.name,
            "DOI(s)": exp.paper_doi,
            "title(s)": titles,
            "publishers":publishers,
            "adsorbent":exp.adsorbent.name,
            "pure_isotherms":pure_isotherms,
            "mixture_isotherms":mixture_isotherms,
        }


    data_regression.check(EXPs)


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
